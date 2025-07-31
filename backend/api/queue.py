from backend.utils.db_conn import db_connection
from flask import Blueprint, jsonify
from psycopg2.extras import RealDictCursor
import json

# Endpoint for Queue
queue_bp = Blueprint("queue", __name__)


# Fetch all users from the database
@queue_bp.route("/api/queue", methods=["GET"])
def get_queue():
    try:
        # Establish connection to database
        conn = db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM queue ORDER BY created_at;")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(rows), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ! CHECK IF USER IS IN QUEUE, IF USER LAST_SCRAPED IS NULL (Edge case), THEN UPDATE THE USER IN QUEUE TO HAVE A DEPTH OF 1
# @users_bp.route("/api/users/create", methods=["POST"])
