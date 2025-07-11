import time

# from utils.db_conn import db_connection


class ScraperWorker:
    def run(self):
        while True:
            print("Worker has been started")

            #  Fetch first user from queue

            #  Check if user is in database? = FALSE
            #       Create the user, and pull data from Github API (is_enriched == TRUE)

            #  Check if user is in database? = TRUE
            #       Check if user is_enriched? = FALSE (User was enqueued from a sponsorship relation)
            #               Since user is being crawled, enrich user metadata from Github API / gender inference
            #               Set is_enriched to TRUE

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
