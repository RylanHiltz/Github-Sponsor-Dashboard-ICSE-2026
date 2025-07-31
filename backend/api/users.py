from backend.utils.db_conn import db_connection
from flask import Blueprint, jsonify, request
from psycopg2.extras import RealDictCursor
import json

# Endpoint for Users
users_bp = Blueprint("users", __name__)


# Fetch all users from the database
@users_bp.route("/api/users", methods=["GET"])
def get_users():

    try:
        # Get pagination parameters from query string, with defaults
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        offset = (page - 1) * per_page

        search_query = request.args.get("search", "")

        # Filters passed in from the frontend to query the user data
        filters = {
            "gender": request.args.getlist("gender"),
            "type": request.args.getlist("type"),
            "location": request.args.getlist("location"),
        }

        # Sorters passed in from the frontend to sort user data
        sort_fields = request.args.getlist("sortField")
        sort_orders = request.args.getlist("sortOrder")

        # Data dictionary of sortable columns in the user data
        sortable_fields = {
            "username": "u.username",
            "name": "u.name",
            "followers": "u.followers",
            "following": "u.following",
            "public_repos": "u.public_repos",
            "total_sponsors": "total_sponsors",
            "total_sponsoring": "total_sponsoring",
            "estimated_earnings": "estimated_earnings",
        }

        # Establish connection to database
        conn = db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        where_clauses = []
        order_clause = []
        params = []

        # Handle search query
        if search_query:
            where_clauses.append("(u.username ILIKE %s OR u.name ILIKE %s)")
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        # Handle filters
        for key, values in filters.items():
            if values:
                # Handle 'None' from frontend for NULL values in DB
                if "None" in values:
                    values.remove("None")
                    if values:
                        where_clauses.append(f"(u.{key} IN %s OR u.{key} IS NULL)")
                        params.append(tuple(values))
                    else:
                        where_clauses.append(f"u.{key} IS NULL")
                else:
                    placeholders = ",".join(["%s"] * len(values))
                    where_clauses.append(f"u.{key} IN ({placeholders})")
                    params.extend(values)

        # Append is_enriched at the end to only query for users who have full profiles
        where_clauses.append(f"u.is_enriched IS TRUE")
        where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Handle column sorters
        order_by_parts = []
        for i, field in enumerate(sort_fields):
            if field in sortable_fields:
                col_name = sortable_fields[field]
                order = "ASC" if sort_orders[i] == "ascend" else "DESC"
                order_by_parts.append(f"{col_name} {order}")
        # Create the order clause to pass into the data query
        order_clause = (
            f"ORDER BY  {', '.join(order_by_parts)}"
            if order_by_parts
            else "ORDER BY sc.total_sponsors DESC"
        )

        # Query for total count with filters
        count_query = f"SELECT COUNT(DISTINCT u.id) FROM users u {where_clause}"
        print(count_query)
        cur.execute(count_query, tuple(params))
        total_count = cur.fetchone()["count"]

        median_query = """
        SELECT 
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY min_sponsor_cost) 
            AS median_sponsor_cost
        FROM users
        WHERE min_sponsor_cost > 0;
        """
        cur.execute(median_query)
        monthly_median = cur.fetchone()["median_sponsor_cost"]

        data_query = f"""
        SELECT 
            u.id, u.name, u.username, u.type, u.avatar_url, u.profile_url,
            u.gender, u.location, u.public_repos, u.public_gists,
            u.followers, u.following, u.hireable, u.min_sponsor_cost, 
            sc.total_sponsors,
            sc.total_sponsoring,
            -- Use a CASE statement to handle users with a min_sponsor_cost of 0 or NULL
            (
                LEAST(
                    (CASE WHEN u.min_sponsor_cost > 0 THEN u.min_sponsor_cost ELSE {monthly_median} END), 
                    {monthly_median}
                ) * sc.total_sponsors
            ) AS estimated_earnings
        FROM users u
        LEFT JOIN (
            SELECT 
                u.id AS user_id,
                COALESCE(COUNT(DISTINCT s1.sponsor_id), 0) + 
                COALESCE(u.private_sponsor_count, 0) AS total_sponsors,
                COALESCE((
                    SELECT COUNT(DISTINCT s2.sponsored_id)
                    FROM sponsorship s2
                    WHERE s2.sponsor_id = u.id
                ), 0) AS total_sponsoring
            FROM users u
            LEFT JOIN sponsorship s1 ON s1.sponsored_id = u.id
            GROUP BY u.id, u.private_sponsor_count
        ) sc ON sc.user_id = u.id
        {where_clause}
        {order_clause}
        LIMIT %s OFFSET %s;
        """

        final_params = params + [per_page, offset]
        cur.execute(data_query, tuple(final_params))

        rows = cur.fetchall()
        ordered_users = []
        for row in rows:
            ordered_users.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "username": row["username"],
                    "type": row["type"],
                    "gender": row["gender"],
                    "hireable": row["hireable"],
                    "location": row["location"],
                    "avatar_url": row["avatar_url"],
                    "profile_url": row["profile_url"],
                    "following": row["following"],
                    "followers": row["followers"],
                    "public_repos": row["public_repos"],
                    "public_gists": row["public_gists"],
                    "total_sponsors": row["total_sponsors"],
                    "total_sponsoring": row["total_sponsoring"],
                    "min_sponsor_cost": row["min_sponsor_cost"],
                    "estimated_earnings": row["estimated_earnings"],
                }
            )

        response_data = {
            "total": total_count,
            "users": ordered_users,
        }
        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/api/users/location", methods=["GET"])
def get_locations():
    """
    Fetches a distinct, sorted list of user locations.
    This query is optimized for PostgreSQL if an index exists on the `location` column.
    The database query planner should use a 'skip scan' on the index for efficiency.
    """
    try:
        conn = db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # This query leverages an index on the 'location' column for both
        # sorting and finding distinct values efficiently.
        location_query = "SELECT DISTINCT location FROM users WHERE location IS NOT NULL ORDER BY location ASC;"
        cur.execute(location_query)
        location_list = [row["location"] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify(location_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
