from backend.utils.db_conn import db_connection
from flask import Blueprint, jsonify
from psycopg2.extras import RealDictCursor

# Endpoint for Users
stats_bp = Blueprint("stats", __name__)


# Fetch all users from the database
@stats_bp.route("/api/stats/brief", methods=["GET"])
def get_stats():
    try:
        # Establish connection to database
        conn = db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            SELECT COUNT(users.id) FROM users WHERE is_enriched = True
            """
        )
        total_count = cur.fetchone()

        cur.execute(
            """
            SELECT COUNT(sponsorship.id) FROM sponsorship
            """
        )
        total_sponsorships = cur.fetchone()
        cur.close()

        res = {
            "total_users": total_count,
            "total_sponsorships": total_sponsorships,
        }
        return jsonify(res), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
