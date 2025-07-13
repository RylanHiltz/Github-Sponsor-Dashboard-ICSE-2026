import time
from backend.utils.db_conn import db_connection

# DB Queries
from backend.db.queries import getFirstInQueue, findUser


class ScraperWorker:
    def run(self):

        # Establish database connection
        conn = db_connection()
        print("Worker has been started")

        while True:
            #  Fetch first user from queue
            data = getFirstInQueue(db=conn)

            #  Check if user is in database? = FALSE
            user_exists = findUser(username=data["username"], db=conn)
            if not user_exists:
                # Create the user, and pull data from Github API (is_enriched == TRUE)
                continue
            else:
                # Check if user is in database? = TRUE
                #       Check if user is_enriched? = FALSE (User was enqueued from a sponsorship relation)
                #       Since user is being crawled, enrich user metadata from Github API / gender inference
                #       Set is_enriched to TRUE
                continue

            # !User should not be is_enriched, and waiting for queue, this does not follow the logic and should never happen!

            #  Crawl the user for sponsorship relations (bi-directional)
            #       Add users and organizations to the users table & queue (minimal data, name and user type; is_enriched defaults to FALSE)
            #       Add sponsorship relations to the database
            #       Increment the depth by 1? (still need to figure out this logic)

            #  Collect the user activity from the Github API (potentially a lot of API requests)

            # ?Log API usage, maybe add feature to pause worker if the api runs out mid way scraping to preserve data?

            #  Set last_scraped to the current time

            #  Check next user in queue if it is not null

            time.sleep(5)  # Wait before checking queue again


if __name__ == "__main__":
    worker = ScraperWorker()
    worker.run()
