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
            WITH total_users_cte AS (
                SELECT COUNT(id) as total_users FROM users WHERE is_enriched = True
            ),
            total_sponsorships_cte AS (
                SELECT COUNT(id) as total_sponsorships FROM sponsorship
            ),
            sponsoring_counts AS (
                SELECT
                    sponsor_id,
                    COUNT(sponsored_id) AS total_sponsoring
                FROM sponsorship
                GROUP BY sponsor_id
            ),
            top_sponsoring_cte AS (
                SELECT
                    u.username,
                    u.avatar_url,
                    sc.total_sponsoring
                FROM sponsoring_counts sc
                JOIN users u ON u.id = sc.sponsor_id
                ORDER BY sc.total_sponsoring DESC
                LIMIT 1
            ),
            sponsored_counts AS (
                SELECT
                    sponsored_id,
                    COUNT(sponsor_id) AS public_sponsors
                FROM sponsorship
                GROUP BY sponsored_id
            ),
            top_sponsored_cte AS (
                SELECT
                    u.username,
                    u.avatar_url,
                    COALESCE(sc.public_sponsors, 0) + COALESCE(u.private_sponsor_count, 0) AS total_sponsors
                FROM users u
                LEFT JOIN sponsored_counts sc ON u.id = sc.sponsored_id
                ORDER BY total_sponsors DESC
                LIMIT 1
            )
            SELECT
                (SELECT total_users FROM total_users_cte) as total_users,
                (SELECT total_sponsorships FROM total_sponsorships_cte) as total_sponsorships,
                (SELECT row_to_json(top_sponsoring_cte) FROM top_sponsoring_cte) as top_sponsoring,
                (SELECT row_to_json(top_sponsored_cte) FROM top_sponsored_cte) as top_sponsored;
            """
        )
        stats = cur.fetchone()
        cur.close()
        conn.close()

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
