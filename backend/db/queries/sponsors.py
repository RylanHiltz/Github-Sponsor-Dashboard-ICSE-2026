from backend.db.queries.users import batchGetUserId
import logging

# This module provides functions for managing sponsorship relationships between users in the database.


# Batch create a sponsored relations for a specific user
def createSponsors(sponsored, sponsor_arr, db):
    entries = [(sponsor, sponsored) for sponsor in sponsor_arr]

    with db.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO sponsorship (sponsor_id, sponsored_id)
            VALUES (%s, %s)
            ON CONFLICT (sponsor_id, sponsored_id) DO NOTHING
            """,
            entries,
        )
    db.commit()
    cur.close()
    return


# Batch create all sponsoring relations for a specific user
def createSponsoring(sponsor, sponsored_arr, db):

    entries = [(sponsor, sponsored) for sponsored in sponsored_arr]

    with db.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO sponsorship (sponsor_id, sponsored_id)
            VALUES (%s, %s)
            ON CONFLICT (sponsor_id, sponsored_id) DO NOTHING
            """,
            entries,
        )
    db.commit()
    cur.close()
    return


# Handles comparison logic between old sponsors and newly crawled, removing where applicable
def syncSponsors(user_id, scraped_sponsors, db):
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT u.username
            FROM sponsorship s
            JOIN users u ON u.id = s.sponsor_id
            WHERE s.sponsored_id = %s
            """,
            (user_id,),
        )
        current_sponsors = {row[0] for row in cur.fetchall()}

    scraped_sponsors = set(scraped_sponsors)

    # Sponsors who exist in the DB, but who are not currently sponsoring the user
    sponsors_to_remove = current_sponsors - scraped_sponsors
    # Sponsors who exist in the scraped list, but have not been added to DB
    sponsors_to_add = scraped_sponsors - current_sponsors

    # Remove old sponsors
    if sponsors_to_remove:
        with db.cursor() as cur:
            cur.execute(
                """
                DELETE FROM sponsorship
                WHERE sponsored_id = %s AND sponsor_id IN (
                    SELECT id FROM users WHERE username = ANY(%s)
                )
                """,
                (user_id, list(sponsors_to_remove)),
            )

    # Insert new sponsor relations
    if sponsors_to_add:
        sponsor_ids = batchGetUserId(list(sponsors_to_add), db)
        createSponsors(user_id, sponsor_arr=sponsor_ids, db=db)
        logging.info(f"Created Sponsor Relations")
    return


# Handles comparison logic between old sponsored users and newly crawled, removing where applicable
def syncSponsorships(user_id, scraped_sponsoring, db):
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT u.username
            FROM sponsorship s
            JOIN users u ON u.id = s.sponsored_id
            WHERE s.sponsor_id = %s
            """,
            (user_id,),
        )
        current_sponsoring = {row[0] for row in cur.fetchall()}

    scraped_sponsoring = set(scraped_sponsoring)

    # Sponsored users who exist in the DB, but who are not currently being sponsored anymore
    sponsoring_to_remove = current_sponsoring - scraped_sponsoring
    # Sponsored users who exist in the scraped list, but have not been added to DB
    sponsoring_to_add = scraped_sponsoring - current_sponsoring

    # Remove old sponsored users
    if sponsoring_to_remove:
        with db.cursor() as cur:
            cur.execute(
                """
                DELETE FROM sponsorship
                WHERE sponsor_id = %s AND sponsored_id IN (
                    SELECT id FROM users WHERE username = ANY(%s)
                )
                """,
                (user_id, list(sponsoring_to_remove)),
            )

    # Insert new sponsoring relations
    if sponsoring_to_add:
        sponsoring_ids = batchGetUserId(list(sponsoring_to_add), db)
        createSponsoring(user_id, sponsored_arr=sponsoring_ids, db=db)
        logging.info(f"Created Sponsoring Relations")
    return


# Occurs if a user has 1 or many sponsor relations attached to previous users but Github returns
# 404 error when user is being enriched. Check sponsor relations, grab sponsored ids, and add
# 1 to each private_sponsor count, delete sponsor relations, and delete user from users and queue.
def notFoundWithSponsors(username, db):
    with db.cursor() as cur:

        # Selects the sponsored IDs attachted to the not found user
        cur.execute(
            """
            SELECT sponsored_id FROM sponsorship 
            WHERE sponsor_id = (SELECT id FROM users WHERE username = %s);
            """,
            (username,),
        )
        rows = cur.fetchall()
        ids = [row[0] for row in rows]
        if ids:
            # updates private sponsor count
            cur.execute(
                """
                UPDATE users
                SET private_sponsor_count = private_sponsor_count + 1
                WHERE id = ANY(%s);
                """,
                (ids,),
            )
            # Delete sponsorships that belong to the user who is not found
            cur.execute(
                """
                DELETE FROM sponsorship 
                WHERE sponsor_id = (SELECT id FROM users WHERE username = %s);
                """,
                (username,),
            )
        db.commit()
    return
