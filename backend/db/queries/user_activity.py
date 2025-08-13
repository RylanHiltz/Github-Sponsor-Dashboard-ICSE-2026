# ENV Imports
from dotenv import load_dotenv
import os

# Functional Imports
from backend.utils.github_api import postRequest
from datetime import datetime
import json
import base64

# Logging Imports
import logging
import time
from backend.logs.logger_config import log_section

# Load sensitive variables
load_dotenv()
URL = "https://api.github.com/graphql"
GITHUB_TOKEN = os.getenv("PAT")


# Return the last year of user activity for the passed in user (PR, commits, issues)
def getUserActivity(github_id, user_id, user_type, created_at, db=None):

    start = int(time.time())

    # Get year account was created from datetime string
    node_id = base64.b64encode(f"04:User{github_id}".encode("utf-8")).decode("utf-8")
    dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    creation_year = dt.year
    current_year = datetime.now().year

    with db.cursor() as cur:

        # If the user is type org, the account cannot have any of the specified user activities
        if user_type == "Organization":
            logging.info(
                f"Account is of type {user_type}, No user activity available to query."
            )
            return

        log_section(f"Collecting User Activity Data via GraphQL")
        query_template = """
        query($node_id: ID!, $from: DateTime!, $to: DateTime!) {
            node(id: $node_id) {
                ... on User {
                    contributionsCollection(from: $from, to: $to) {
                        totalCommitContributions,
                        totalPullRequestContributions,
                        totalIssueContributions,
                        totalPullRequestReviewContributions
                    }
                }
            }
        }
        """

        for year in range(creation_year, current_year + 1):
            try:

                from_date = f"{year}-01-01T00:00:00Z"
                to_date = f"{year}-12-31T23:59:59Z"
                variables = {"node_id": node_id, "from": from_date, "to": to_date}

                query = {"query": query_template, "variables": variables}

                response = postRequest(URL, json=query)
                response.raise_for_status()  # Raise an exception for bad status codes
                data = response.json()

                if "errors" in data:
                    logging.error(
                        f"GraphQL Error for user at year ({year}): {data['errors']}"
                    )
                    continue  # Skip to the next year on error

                # CORRECTED: Look for 'node' instead of 'user'
                contributions = (
                    data.get("data", {}).get("node", {}).get("contributionsCollection")
                )

                if contributions:
                    # Create a dictionary of the user stats to grab
                    stats = {
                        "commits": contributions.get("totalCommitContributions", 0),
                        "pull_requests": contributions.get(
                            "totalPullRequestContributions", 0
                        ),
                        "issues": contributions.get("totalIssueContributions", 0),
                        "reviews": contributions.get(
                            "totalPullRequestReviewContributions", 0
                        ),
                    }
                else:
                    logging.warning(
                        f"No contribution data for user in {year}. Inserting zero record."
                    )
                    stats = {
                        "commits": 0,
                        "pull_requests": 0,
                        "issues": 0,
                        "reviews": 0,
                    }

                # Convert the dictionary to a JSON string. This works for both JSON and JSONB columns.
                stats_json = json.dumps(stats)

                logging.info(f" -> Year {year}: {stats_json}")

                cur.execute(
                    """
                    INSERT INTO user_activity (user_id, year, activity_data)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id, year) DO UPDATE SET
                        activity_data = EXCLUDED.activity_data,
                        last_updated = NOW();
                    """,
                    (user_id, year, stats_json),
                )

            except Exception as e:
                logging.error(
                    f"An unexpected error occurred for user at year ({year}): {e}"
                )
                continue  # Skip to next year
    db.commit()
    cur.close()
    end = int(time.time())
    elapsed = end - start
    logging.info(f"User Activity Data Collected: Elapsed {elapsed:.2f} seconds")
    return


def getTotalUserActivity(user_id, db):

    with db.cursor() as cur:
        cur.execute(
            """
            SELECT
                    SUM((activity_data->>'commits')::BIGINT),
                    SUM((activity_data->>'pull_requests')::BIGINT),
                    SUM((activity_data->>'issues')::BIGINT),
                    SUM((activity_data->>'reviews')::BIGINT)
                FROM
                    user_activity
                WHERE
                    user_id = %s;
                """,
            (user_id,),
        )
        result = cur.fetchone()
        if result and result[0] is not None:
            return {
                "total_commits": result[0],
                "total_pull_requests": result[1],
                "total_issues": result[2],
                "total_reviews": result[3],
            }
    # Return zero values if no activity is found
    return {
        "total_commits": 0,
        "total_pull_requests": 0,
        "total_issues": 0,
        "total_reviews": 0,
    }


def refreshActivityCheck(user_id, db):
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT
                COALESCE(MAX(last_updated), 'epoch'::timestamp) < NOW() - INTERVAL '365 days'
            FROM
                user_activity
            WHERE
                user_id = %s;
            """,
            (user_id,),
        )
        result = cur.fetchone()
        print(result)
        # The query returns a tuple with a single boolean value, e.g., (True,).
        # We need to extract the boolean from the tuple.
        return result[0] if result is not None else True
