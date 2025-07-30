import requests
from dotenv import load_dotenv
import os
import logging
from flask import jsonify
import json
import time
from backend.utils.github_api import postRequest
from backend.logs.logger_config import log_section
from datetime import datetime, timezone

# Load sensitive variables
load_dotenv()
URL = "https://api.github.com/graphql"
GITHUB_TOKEN = os.getenv("PAT")


# Return the last year of user activity for the passed in user (PR, commits, issues)
def getUserActivity(username, user_id, user_type, created_at, db=None):

    start = int(time.time())

    # Get year account was created from datetime string
    dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    creation_year = dt.year
    current_year = datetime.now().year

    with db.cursor() as cur:

        # If the user is type org, the account cannot have any of the specified user activities
        if user_type == "Organization":
            logging.info(
                f"{username} is account type {user_type}, No user activity available to query."
            )
            return

        log_section(f"Collecting User Activity Data For: {username} via GraphQL")
        print(f"\nCollecting User Activity Data For: '{username}'")

        query_template = """
        query($username: String!, $from: DateTime!, $to: DateTime!) {
            user(login: $username) {
                contributionsCollection(from: $from, to: $to) {
                totalCommitContributions, totalPullRequestContributions, totalIssueContributions, totalPullRequestReviewContributions
                }
            }
        }
        """

        for year in range(creation_year, current_year + 1):
            try:

                from_date = f"{year}-01-01T00:00:00Z"
                to_date = f"{year}-12-31T23:59:59Z"
                variables = {"username": username, "from": from_date, "to": to_date}

                query = {"query": query_template, "variables": variables}

                response = postRequest(URL, json=query)
                response.raise_for_status()  # Raise an exception for bad status codes
                data = response.json()

                if "errors" in data:
                    logging.error(
                        f"GraphQL Error for {username} ({year}): {data['errors']}"
                    )
                    continue  # Skip to the next year on error

                contributions = (
                    data.get("data", {}).get("user", {}).get("contributionsCollection")
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
                        f"No contribution data for {username} in {year}. Inserting zero record."
                    )
                    stats = {
                        "commits": 0,
                        "pull_requests": 0,
                        "issues": 0,
                        "code_reviews": 0,
                    }

                # Convert the dictionary to a JSON string. This works for both JSON and JSONB columns.
                stats_json = json.dumps(stats)
                print(stats_json)

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
                    f"An unexpected error occurred for {username} ({year}): {e}"
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
