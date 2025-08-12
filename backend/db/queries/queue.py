from backend.utils.db_conn import db_connection
from backend.models.UserModel import UserModel
from dotenv import load_dotenv
from flask import Blueprint, jsonify
from psycopg2.extras import RealDictCursor
import os
import requests


load_dotenv()
GITHUB_TOKEN = os.getenv("PAT")


# def batchGetQueue(db):
#     with db.cursor() as cur:
#         cur.execute(
#             """
#             SELECT username
#             FROM queue
#             WHERE status = 'pending' AND github_id IS NULL
#             ORDER BY created_at ASC, id ASC
#             """
#         )
#         results = cur.fetchall()
#         print(len(results))
#     # Convert list of tuples to list of strings
#     return [row[0] for row in results]


# Batch add an array of usernames to the queue for scraping
def batchAddQueue(github_ids, depth, db):

    entries = [(github_id, depth, "pending") for github_id in github_ids]

    with db.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO queue (github_id, depth, status)
            VALUES (%s, %s, %s)
            ON CONFLICT (github_id) DO NOTHING;
            """,
            entries,
        )
    db.commit()
    cur.close()
    return


def batchRequeue(db):
    with db.cursor() as cur:
        cur.execute(
            """
            UPDATE queue SET
            depth = 1, 
            status = 'pending'
            WHERE status = 'skipped';
            """
        )
    db.commit()
    print("Batch requeued all edge case users at maximum depth as new roots")
    return


# Update status of users to "pending" to crawl again if they exceed days_old created at time
# Resets the created_at time to current time, enqueing them for scraping again (after current queue)
def enqueueStaleUsers(db, days_old):
    with db.cursor() as cur:
        cur.execute(
            """
            UPDATE queue
            SET status = 'pending', created_at = NOW()
            FROM users
            WHERE queue.github_id = users.github_id
            AND queue.status = 'completed'
            AND users.last_scraped < NOW() - INTERVAL '%s days'
            """,
            (days_old,),
        )
        db.commit()


# Gets the first user inside the queue who has status="pending"
def getFirstInQueue(db):
    cur = db.cursor()
    cur.execute(
        """
        SELECT github_id, depth FROM queue
        WHERE status = 'pending'
        ORDER BY created_at ASC, id ASC
        LIMIT 1;
        """
    )
    result = cur.fetchone()
    cur.close()
    if result:
        # Map tuple to dict
        return {"github_id": result[0], "depth": result[1]}
    return None


# Update the status of the passed in user in the DB
def updateStatus(github_id: int, status, db):
    with db.cursor() as cur:
        cur.execute(
            """
            UPDATE queue SET
                status = %s
            WHERE github_id = %s
            """,
            (status, github_id),
        )
        db.commit()
        print(f"Updated user status\n")
        return


# Attempt to add a single username to the queue, check if the user is a real github user, and does not already exist
# Makes a single GraphQL API request to check if 1) account exists, 2) account has > 0 sponsors OR sponsoring
def addToQueue(username, db):
    graphql_query = {
        "query": """
            query($username: String!) {
              user(login: $username) {
                databaseId
                sponsors {
                  totalCount
                }
                sponsoring {
                  totalCount
                }
              }
            }
        """,
        "variables": {"username": username},
    }

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        "https://api.github.com/graphql", json=graphql_query, headers=headers
    )

    if response.status_code != 200:
        return {"success": False, "error": "GitHub API error"}, response.status_code

    data = response.json()
    user_data = data.get("data", {}).get("user")

    if not user_data:
        return {"success": False, "error": "User not found on GitHub"}, 404

    sponsors_count = user_data["sponsors"]["totalCount"]
    sponsoring_count = user_data["sponsoring"]["totalCount"]

    if sponsors_count == 0 and sponsoring_count == 0:
        return {
            "success": False,
            "error": "User has no sponsors and is not sponsoring anyone",
        }, 400

    github_id = user_data["databaseId"]

    # Add user to queue with depth 1 (user is a new root)
    with db.cursor() as cur:
        # Check if github_id already exists in the queue
        cur.execute(
            """
            SELECT 1 FROM queue WHERE github_id = %s
            """,
            (github_id,),
        )
        if cur.fetchone():
            return {"success": False, "error": "User already in queue"}, 409

        # Insert user into queue
        cur.execute(
            """
            INSERT INTO queue (github_id, depth, status)
            VALUES (%s, %s, %s)
            ON CONFLICT (github_id) DO NOTHING;
            """,
            (github_id, 1, "pending"),
        )
        db.commit()
        return {"success": True}, 200


# Delete a user from the queue
def deleteFromQueue(github_id, db):
    with db.cursor() as cur:
        cur.execute(
            """
            DELETE FROM queue
            WHERE github_id = %s;
            """,
            (github_id,),
        )
        db.commit()
        cur.close()
        print(f"Deleted user from queue")
        return
