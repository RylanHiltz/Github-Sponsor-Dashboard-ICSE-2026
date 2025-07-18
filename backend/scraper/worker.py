import time
from backend.utils.db_conn import db_connection

# DB Queries
from backend.db.queries.queue import getFirstInQueue, batchAddQueue, updateStatus
from backend.db.queries.users import (
    createUser,
    enrichUser,
    findUser,
    scrapePronouns,
    batchCreateUser,
    batchGetUserId,
    getUserData,
)
from backend.db.queries.sponsors import createSponsoring, createSponsors
from backend.db.queries.user_activity import getUserActivity

# Scraper
from backend.scraper.utils import scrape_sponsors, scrape_sponsoring

# Authentication for pronoun scraping
from backend.scraper.use_auth import get_auth, is_auth_expiring_soon

import time

MAX_DEPTH = 4


class ScraperWorker:
    def run(self):

        # Establish database connection
        conn = db_connection()
        print("Worker has been started")

        while True:
            start = time.time()

            check_auth = is_auth_expiring_soon()
            # If auth is close to expiration
            if check_auth is True:
                get_auth()

            #  Fetch first user from queue
            data = getFirstInQueue(db=conn)
            if not data:
                time.sleep(5)
                continue

            username = data["username"]
            depth = data["depth"]

            # Check if the user exists
            user_exists, user_id = findUser(username, db=conn)

            # User exists in DB from previous sponsor relation
            if user_exists:
                # Enrich user metadata from Github API / gender inference
                user = enrichUser(username, db=conn)
            # User does not exist in DB, create new user
            else:
                user = createUser(username, db=conn)

            # !User should not be is_enriched, and waiting for queue, this does not follow the logic and should never happen!

            #  Crawl the user for sponsorship relations (bi-directional)
            sponsors, private_sponsor_count = scrape_sponsors(username)
            sponsoring = scrape_sponsoring(username, user.type)
            print("sponsors: ", sponsors)
            print("sponsoring: ", sponsoring)

            unique_users = list(set(sponsors) | set(sponsoring))

            # Add users and organizations to the users table & queue (name and is_enriched defaults to FALSE)
            # Increment the depth by 1? (still need to figure out this logic)
            batchAddQueue(unique_users, depth=(depth + 1), db=conn)
            batchCreateUser(unique_users, db=conn)

            # If the user has sponsors, create the relations in the DB
            if sponsors:
                sponsor_ids = batchGetUserId(sponsors, conn)
                print(sponsor_ids)
                createSponsors(user_id, sponsor_arr=sponsor_ids, db=conn)
            # If the user is sponsoring users, create the relations in the DB
            if sponsoring:
                sponsoring_ids = batchGetUserId(sponsoring, conn)
                print(sponsoring_ids)
                createSponsoring(user_id, sponsored_arr=sponsoring_ids, db=conn)

            # Collect the user activity from the Github API (potentially a lot of API requests)
            getUserActivity(user=username, user_id=user_id, db=conn)

            # Update staus of the crawled user
            updateStatus(user=username, status="completed", db=conn)

            end = time.time()
            elapsed = end - start
            print(f"time for 1 user crawled: {elapsed:.4f}")
            break

            # ?Log API usage, maybe add feature to pause worker if the api runs out mid way scraping to preserve data?
            #  Set last_scraped to the current time
            #  Also set the private sponsor amount in the same function/db call

            time.sleep(5)  # Wait before checking queue again


if __name__ == "__main__":
    worker = ScraperWorker()
    worker.run()
