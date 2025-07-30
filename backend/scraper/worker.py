import time
from backend.utils.db_conn import db_connection
import logging
from pathlib import Path
import logging
import psycopg2

# DB Queries
from backend.db.queries.queue import (
    getFirstInQueue,
    batchAddQueue,
    updateStatus,
    enqueueStaleUsers,
)
from backend.db.queries.users import (
    createUser,
    enrichUser,
    findUser,
    batchCreateUser,
    finalizeUserScrape,
)
from backend.db.queries.sponsors import (
    syncSponsors,
    syncSponsorships,
)
from backend.db.queries.user_activity import getUserActivity

# Scraper
from backend.scraper.utils import get_sponsorships

# Authentication for pronoun scraping
from backend.scraper.use_auth import get_auth, is_auth_expiring_soon

import time

from backend.logs.logger_config import init_logger, log_header

MAX_DEPTH = 4


class ScraperWorker:
    def run(self):

        init_logger()

        # Establish database connection
        conn = db_connection()
        log_header("Worker has Started")

        # Start rescraping timer
        last_stale_check = time.time()

        while True:
            start = time.time()

            check_auth = is_auth_expiring_soon()
            # If auth is close to expiration
            if check_auth is True:
                get_auth()

            # Check last_stale_check every 4 hours
            if time.time() - last_stale_check >= 14400:
                # Re-scrape users every 2 weeks
                enqueueStaleUsers(conn, days_old=14)
                last_stale_check = time.time()
                # Re-establish DB connection every 4 hours
                conn = db_connection()
                logging.info(
                    "4 Hours Elapsed: Re-establishing Fresh Database Connection."
                )

            try:
                #  Fetch first user from queue
                data = getFirstInQueue(db=conn)
                if not data:
                    time.sleep(5)
                    continue

                username = data["username"]
                depth = data["depth"]
                log_header(f"SCRAPING CURRENT USER: {username} ")
                print(f"\n\nProcessing user: {username} at depth: {depth}")

                # If the users depth exceeds MAX_DEPTH to crawl, skip the user and continue to next in queue
                if depth > MAX_DEPTH:
                    updateStatus(username, "skipped")
                    logging.info(f"Skipped user: {username}, Max Depth Reached.")
                    continue

                # Check if the user exists and if the user is enriched with REST API data
                user_exists, is_enriched, user_id, identity_data = findUser(
                    username=username, db=conn
                )
                print(user_exists, is_enriched, user_id, identity_data)

                try:
                    # User exists in DB from previous sponsor relation
                    if user_exists and is_enriched == False:
                        # Enrich user metadata from Github API / gender inference
                        user = enrichUser(username, db=conn)
                        logging.info(f"Processing User: {username} at depth: {depth}")

                    # User has already been scraped for their data once (prevents unwanted future updates)
                    elif user_exists and is_enriched == True:
                        user = enrichUser(
                            username,
                            db=conn,
                            enriched=is_enriched,
                            identity=identity_data,
                        )
                        logging.info(
                            f"User already enriched: {username} at depth: {depth}, Data has been refreshed."
                        )

                    # User does not exist in DB, create new user
                    elif not user_exists:
                        user, user_id = createUser(username, db=conn)
                        logging.info(f"Creating User: {username} at depth: {depth}")

                except ValueError as e:
                    logging.warning(
                        "User has been deleted. They do not exist on github (sponsors if previously existed have been updated)"
                    )
                    continue

                #  Crawl the user for sponsorship relations
                print("Getting Sponsorships from GraphQL API:")
                sponsors, sponsoring, private_count, min_sponsor_tier = (
                    get_sponsorships(username, user.type)
                )

                # Create a list of only the unique usernames
                # This is important if bi-directional sponsor relations exist
                unique_users = list(set(sponsors) | set(sponsoring))

                # Batch create unique users who are not present in the table
                batchAddQueue(unique_users, depth=(depth + 1), db=conn)
                batchCreateUser(unique_users, db=conn)

                # Add users and organizations to the users table & queue (name and is_enriched defaults to FALSE)
                syncSponsors(user_id, sponsors, conn)
                syncSponsorships(user_id, sponsoring, conn)

                # Collect the user activity from the Github API (potentially a lot of API requests)
                getUserActivity(
                    username=username,
                    user_id=user_id,
                    user_type=user.type,
                    created_at=user.github_created_at,
                    db=conn,
                )

                # Update staus of the crawled user
                updateStatus(user=username, status="completed", db=conn)

                # Set last_scraped to the current time
                finalizeUserScrape(username, private_count, min_sponsor_tier, conn)

                # Print the elapsed time taken to crawl the current user
                end = time.time()
                elapsed = end - start
                logging.info(f"user {username} crawled: {elapsed:.2f} seconds elapsed")

                time.sleep(1)  # Wait before checking queue again

            # Handle operational error thrown by DB
            except psycopg2.OperationalError as e:
                logging.warning(f"DB connection lost: {e}. Reconnecting...")
                conn = db_connection()
                continue
            # If another error occurs, log the error and stop the scraper
            except Exception as e:
                logging.error(f"Unhandled exception: {e}", exc_info=True)
                time.sleep(10)
                break


if __name__ == "__main__":
    worker = ScraperWorker()
    worker.run()
