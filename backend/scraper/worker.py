import time
from backend.utils.db_conn import db_connection

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
    scrapePronouns,
    batchCreateUser,
    batchGetUserId,
    getUserData,
    finalizeUserScrape,
)
from backend.db.queries.sponsors import (
    createSponsoring,
    createSponsors,
    syncSponsors,
    syncSponsorships,
)
from backend.db.queries.user_activity import getUserActivity

# Scraper
from backend.scraper.utils import scrape_sponsors, scrape_sponsoring

# Authentication for pronoun scraping
from backend.scraper.use_auth import get_auth, is_auth_expiring_soon

import time

MAX_DEPTH = 4


# ! DELETE ALL OF THE USERS, THIS DATA WAS WRONG CAUSE OF THE SPONSORING SCRAPER LOGIC NOT PAGINATING NDOIJEWHFDB KLWJEFBGEK


class ScraperWorker:
    def run(self):

        # Establish database connection
        conn = db_connection()
        print("Worker has been started")

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
                enqueueStaleUsers(conn, days_old=28)
                last_stale_check = time.time()
                # Re-establish DB connection every 4 hours
                conn = db_connection()

            #  Fetch first user from queue
            data = getFirstInQueue(db=conn)
            if not data:
                time.sleep(5)
                continue

            username = data["username"]
            depth = data["depth"]

            # If the users depth exceeds MAX_DEPTH to crawl, skip the user and continue to next in queue
            if depth > MAX_DEPTH:
                updateStatus(username, "skipped")
                continue

            # Check if the user exists
            user_exists = findUser(username, db=conn)

            # User exists in DB from previous sponsor relation
            if user_exists:
                # Enrich user metadata from Github API / gender inference
                user, user_id = enrichUser(username, db=conn)
            # User does not exist in DB, create new user
            else:
                user, user_id = createUser(username, db=conn)

            # !User should not be is_enriched, and "pending" in queue, this does not follow the logic and should never happen!

            #  Crawl the user for sponsorship relations (bi-directional)
            sponsors, private_sponsor_count = scrape_sponsors(username)
            sponsoring = scrape_sponsoring(username, user.type)

            # Add users and organizations to the users table & queue (name and is_enriched defaults to FALSE)
            if sponsors:
                batchAddQueue(sponsors, depth=(depth + 1), db=conn)
                batchCreateUser(sponsors, db=conn)
                syncSponsors(user_id, sponsors, conn)
            if sponsoring:
                batchAddQueue(sponsoring, depth=(depth + 1), db=conn)
                batchCreateUser(sponsoring, db=conn)
                syncSponsorships(user_id, sponsoring, conn)

            # Collect the user activity from the Github API (potentially a lot of API requests)
            getUserActivity(
                user=username, user_id=user_id, user_type=user.type, db=conn
            )

            # Update staus of the crawled user
            updateStatus(user=username, status="completed", db=conn)

            # Set last_scraped to the current time
            finalizeUserScrape(username, private_sponsor_count, conn)

            # Print the elapsed time taken to crawl the current user
            end = time.time()
            elapsed = end - start
            print(f"user {username} crawled: {elapsed:.4f} seconds elapsed")

            time.sleep(3)  # Wait before checking queue again


if __name__ == "__main__":
    worker = ScraperWorker()
    worker.run()
