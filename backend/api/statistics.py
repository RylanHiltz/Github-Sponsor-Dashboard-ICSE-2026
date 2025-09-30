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
           WITH sponsored_counts AS (
    SELECT sponsored_id AS user_id, COUNT(DISTINCT sponsor_id) AS public_sponsors
    FROM sponsorship
    GROUP BY sponsored_id
),
sponsoring_counts AS (
    SELECT sponsor_id AS user_id, COUNT(DISTINCT sponsored_id) AS total_sponsoring
    FROM sponsorship
    GROUP BY sponsor_id
),
sponsorship_counts AS (
    SELECT 
        u.id AS user_id,
        COALESCE(sc.public_sponsors, 0) + COALESCE(u.private_sponsor_count, 0) AS total_sponsors,
        COALESCE(gc.total_sponsoring, 0) AS total_sponsoring
    FROM users u
    LEFT JOIN sponsored_counts sc ON u.id = sc.user_id
    LEFT JOIN sponsoring_counts gc ON u.id = gc.user_id
),
total_users_cte AS (
    SELECT COUNT(DISTINCT u.id) AS total_users
    FROM users u
    JOIN sponsorship_counts sc ON u.id = sc.user_id
    WHERE u.is_enriched IS TRUE
      AND (sc.total_sponsors > 0 OR sc.total_sponsoring > 0)
),
total_sponsorships_cte AS (
    SELECT COUNT(*) as total_sponsorships
    FROM sponsorship
),
top_sponsoring_cte AS (
    SELECT u.username, u.avatar_url, sc.total_sponsoring
    FROM sponsorship_counts sc
    JOIN users u ON u.id = sc.user_id
    ORDER BY sc.total_sponsoring DESC
    LIMIT 1
),
top_sponsored_cte AS (
    SELECT u.username, u.avatar_url, sc.total_sponsors
    FROM sponsorship_counts sc
    JOIN users u ON u.id = sc.user_id
    ORDER BY sc.total_sponsors DESC
    LIMIT 1
)
SELECT
    (SELECT total_users FROM total_users_cte) AS total_users,
    (SELECT total_sponsorships FROM total_sponsorships_cte) AS total_sponsorships,
    (SELECT row_to_json(top_sponsoring_cte) FROM top_sponsoring_cte) AS top_sponsoring,
    (SELECT row_to_json(top_sponsored_cte) FROM top_sponsored_cte) AS top_sponsored;
            """
        )
        stats = cur.fetchone()
        cur.close()
        conn.close()

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stats_bp.route("/api/user-stats", methods=["GET"])
def get_location_dist():
    try:
        conn = db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            WITH sponsored_user_ids AS (
                -- First, get a distinct list of all user IDs involved in sponsorships
                SELECT sponsored_id AS user_id FROM sponsorship
                UNION
                SELECT sponsor_id AS user_id FROM sponsorship
            ),
            user_gender_by_country AS (
                -- Then, join that list with the users table
                SELECT
                    u.location AS country,
                    -- Use the more efficient FILTER clause for conditional aggregation
                    COUNT(*) FILTER (WHERE u.gender = 'Male') AS male,
                    COUNT(*) FILTER (WHERE u.gender = 'Female') AS female,
                    COUNT(*) FILTER (WHERE u.gender = 'Other') AS other,
                    COUNT(*) FILTER (WHERE u.gender = 'Unknown' OR u.gender IS NULL) AS unknown
                FROM users u
                JOIN sponsored_user_ids s ON u.id = s.user_id
                WHERE u.location IS NOT NULL
                GROUP BY u.location
            )
            SELECT
                ug.country,
                json_build_object(
                    'male', ug.male,
                    'female', ug.female,
                    'other', ug.other,
                    'unknown', ug.unknown
                ) AS "genderData"
            FROM user_gender_by_country ug
            ORDER BY (ug.male + ug.female + ug.other + ug.unknown) DESC;
            """
        )
        stats = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get Gender Distribution
@stats_bp.route("/api/gender-stats", methods=["GET"])
def get_gender_stats():
    try:
        conn = db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            WITH active_users AS (
            SELECT sponsor_id AS user_id FROM sponsorship
            UNION
            SELECT sponsored_id AS user_id FROM sponsorship
            )
            SELECT 
            COALESCE(u.gender, 'Unknown') AS gender,
            COUNT(*) AS count
            FROM users u
            JOIN active_users au ON u.id = au.user_id
            WHERE (u.type = 'User') AND (u.has_pronouns = TRUE)
            GROUP BY COALESCE(u.gender, 'Unknown');
            """
        )
        stats = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stats_bp.route("/api/user-sponsorship-stats", methods=["GET"])
def get_sponsorship_stats():
    try:
        conn = db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            WITH user_roles AS (
            SELECT 
                user_id,
                BOOL_OR(role = 'sponsor') AS is_sponsoring,
                BOOL_OR(role = 'sponsored') AS is_sponsored
            FROM (
                SELECT sponsor_id AS user_id, 'sponsor' AS role FROM sponsorship
                UNION ALL
                SELECT sponsored_id AS user_id, 'sponsored' AS role FROM sponsorship
                UNION ALL
                SELECT id AS user_id, 'sponsored' AS role FROM users WHERE private_sponsor_count > 0
            ) AS roles
            GROUP BY user_id
            )
            SELECT
            COUNT(*) FILTER (
                WHERE is_sponsoring AND NOT is_sponsored
                AND EXISTS (
                SELECT 1 FROM users u WHERE u.id = user_roles.user_id AND u.type = 'User'
                )
            ) AS sponsoring_only,
            COUNT(*) FILTER (
                WHERE is_sponsored AND NOT is_sponsoring
                AND EXISTS (
                SELECT 1 FROM users u WHERE u.id = user_roles.user_id AND u.type = 'User'
                )
            ) AS sponsored_only,
            COUNT(*) FILTER (
                WHERE is_sponsoring AND is_sponsored
                AND EXISTS (
                SELECT 1 FROM users u WHERE u.id = user_roles.user_id AND u.type = 'User'
                )
            ) AS both
            FROM user_roles;
            """
        )
        stats = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stats_bp.route("/api/brief-user-stats", methods=["GET"])
def get_user_brief_stats():
    try:
        conn = db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
WITH user_type_users AS (
    SELECT id, username, avatar_url, location, private_sponsor_count
    FROM users
    WHERE type = 'User'
),
sponsored_counts AS (
    SELECT sponsored_id AS user_id, COUNT(DISTINCT sponsor_id) AS public_sponsors
    FROM sponsorship
    GROUP BY sponsored_id
),
sponsoring_counts AS (
    SELECT sponsor_id AS user_id, COUNT(DISTINCT sponsored_id) AS total_sponsoring
    FROM sponsorship
    GROUP BY sponsor_id
),
sponsorship_counts AS (
    SELECT 
        u.id AS user_id,
        COALESCE(sc.public_sponsors, 0) + COALESCE(u.private_sponsor_count, 0) AS total_sponsors,
        COALESCE(gc.total_sponsoring, 0) AS total_sponsoring
    FROM user_type_users u
    LEFT JOIN sponsored_counts sc ON u.id = sc.user_id
    LEFT JOIN sponsoring_counts gc ON u.id = gc.user_id
),
top_sponsored AS (
    SELECT 
        u.username,
        u.avatar_url,
        sc.total_sponsors
    FROM user_type_users u
    JOIN sponsorship_counts sc ON u.id = sc.user_id
    ORDER BY sc.total_sponsors DESC
    LIMIT 1
),
top_sponsoring AS (
    SELECT 
        u.username,
        u.avatar_url,
        sc.total_sponsoring
    FROM user_type_users u
    JOIN sponsorship_counts sc ON u.id = sc.user_id
    ORDER BY sc.total_sponsoring DESC
    LIMIT 1
),
country_sponsored_counts AS (
    -- Include users who have public sponsors OR only private sponsors
    SELECT 
        u.location AS country,
        COUNT(DISTINCT u.id) AS sponsored_users
    FROM user_type_users u
    JOIN sponsorship_counts sc ON u.id = sc.user_id
    WHERE u.location IS NOT NULL
      AND sc.total_sponsors > 0
    GROUP BY u.location
),
top_country AS (
    SELECT country, sponsored_users
    FROM country_sponsored_counts
    ORDER BY sponsored_users DESC
    LIMIT 1
)
SELECT
    (SELECT COUNT(DISTINCT u.id) 
     FROM user_type_users u
     JOIN sponsorship_counts sc ON u.id = sc.user_id
     WHERE sc.total_sponsors > 0 OR sc.total_sponsoring > 0) AS total_users,
    (SELECT row_to_json(top_sponsored) FROM top_sponsored) AS most_sponsored_user,
    (SELECT row_to_json(top_sponsoring) FROM top_sponsoring) AS most_sponsoring_user,
    (SELECT row_to_json(top_country) FROM top_country) AS top_country;
            """
        )
        results = cur.fetchall()
        stats = results[0] or None
        cur.close()
        conn.close()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
