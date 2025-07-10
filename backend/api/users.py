from utils.db_conn import db_connection
from flask import Blueprint, jsonify
from psycopg2.extras import RealDictCursor
import json

# Endpoint for Users
users_bp = Blueprint("users", __name__)


# Fetch all users from the database
@users_bp.route("/api/users", methods=["GET"])
def get_all_users():
    try:
        # Establish connection to database
        conn = db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users ORDER BY id;")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(rows), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/api/users/create", methods=["POST"])
def create_user():

    return
