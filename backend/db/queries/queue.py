from backend.utils.db_conn import db_connection
from backend.models.github_user import UserModel
from dotenv import load_dotenv
from flask import Blueprint, jsonify
from psycopg2.extras import RealDictCursor
import os
import requests


# Batch add an array of usernames to the queue for scraping
def batchAddQueue(usernames, type, db):
    return


# Gets the first user inside the queue who has status="pending"
def getFirstInQueue(db):
    cur = db.cursor()
    cur.execute(
        """
        SELECT username, depth, type FROM queue
        WHERE status = 'pending'
        ORDER BY created_at ASC
        LIMIT 1;
        """
    )
    result = cur.fetchone()
    cur.close()
    if result:
        # Map tuple to dict
        return {"username": result[0], "depth": result[1], "type": result[2]}
    return None


def updateStatus(user, status, db):
    return
