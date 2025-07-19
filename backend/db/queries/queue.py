from backend.utils.db_conn import db_connection
from backend.models.github_user import UserModel
from dotenv import load_dotenv
from flask import Blueprint, jsonify
from psycopg2.extras import RealDictCursor
import os
import requests


load_dotenv()
GITHUB_TOKEN = os.getenv("PAT")


# Batch add an array of usernames to the queue for scraping
def batchAddQueue(usernames, depth, db):

    entries = [(username, depth, "pending") for username in usernames]

    with db.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO queue (username, depth, status)
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO NOTHING;
            """,
            entries,
        )
    db.commit()
    cur.close()
    return


# Gets the first user inside the queue who has status="pending"
def getFirstInQueue(db):
    cur = db.cursor()
    cur.execute(
        """
        SELECT username, depth FROM queue
        WHERE status = 'pending'
        ORDER BY created_at ASC
        LIMIT 1;
        """
    )
    result = cur.fetchone()
    cur.close()
    if result:
        # Map tuple to dict
        return {"username": result[0], "depth": result[1]}
    return None


# Update the status of the passed in user in the DB
def updateStatus(user, status, db):
    with db.cursor() as cur:
        cur.execute(
            """
            UPDATE queue SET
                status = %s
            WHERE username = %s
            """,
            (status, user),
        )
        db.commit()
        cur.close()
        print(f"Updated user status {user}")
        return


def addToQueue(username, db):
    url = f"https://api.github.com/users/{username}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.get(url=url, headers=headers)

    if response.status_code == 404:
        return {"success": False, "error": "User not found on GitHub"}, 404

    if response.status_code != 200:
        return {"success": False, "error": "GitHub API error"}, response.status_code

    # Add user to queue with depth 1 (user is a new root)
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO queue (username, depth, status) VALUES (%s, %s, %s)
            ON CONFLICT (username) DO NOTHING
            """,
            (username, 1, "pending"),
        )
        db.commit()
        cur.close()
        return {"success": True}, 200


def deleteFromQueue(username, db):
    with db.cursor() as cur:
        cur.execute(
            """
            DELETE FROM queue
            WHERE username = %s;
            """,
            (username),
        )
        db.commit()
        cur.close()
        print(f"Deleted {username} from queue")
        return
