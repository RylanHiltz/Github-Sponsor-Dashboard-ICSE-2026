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


# * REFACTORED FOR GITHUB ID
# Handles comparison logic between old sponsors and newly crawled, removing where applicable
def syncSponsors(user_id, latest_sponsor_ids, db):
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT u.github_id
            FROM sponsorship s
            JOIN users u ON u.id = s.sponsor_id
            WHERE s.sponsored_id = %s
            """,
            (user_id,),
        )
        existing_sponsors = {row[0] for row in cur.fetchall()}

    latest_sponsor_ids = set(latest_sponsor_ids)

    # Sponsors who exist in the DB, but who are not currently sponsoring the user
    sponsors_to_remove = existing_sponsors - latest_sponsor_ids
    # Sponsors who exist in the scraped list, but have not been added to DB
    sponsors_to_add = latest_sponsor_ids - existing_sponsors

    # Remove old sponsors
    if sponsors_to_remove:
        with db.cursor() as cur:
            cur.execute(
                """
                DELETE FROM sponsorship
                WHERE sponsored_id = %s AND sponsor_id IN (
                    SELECT id FROM users WHERE github_id = ANY(%s)
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


# * REFACTORED FOR GITHUB ID
# Handles comparison logic between old sponsored users and newly crawled, removing where applicable
def syncSponsorships(user_id, latest_sponsored_ids, db):
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT u.github_id
            FROM sponsorship s
            JOIN users u ON u.id = s.sponsored_id
            WHERE s.sponsor_id = %s
            """,
            (user_id,),
        )
        existing_sponsored = {row[0] for row in cur.fetchall()}

    latest_sponsored_ids = set(latest_sponsored_ids)

    # Sponsored users who exist in the DB, but who are not currently being sponsored anymore
    sponsoring_to_remove = existing_sponsored - latest_sponsored_ids
    # Sponsored users who exist in the scraped list, but have not been added to DB
    sponsoring_to_add = latest_sponsored_ids - existing_sponsored

    # Remove old sponsored users
    if sponsoring_to_remove:
        with db.cursor() as cur:
            cur.execute(
                """
                DELETE FROM sponsorship
                WHERE sponsor_id = %s AND sponsored_id IN (
                    SELECT id FROM users WHERE github_id = ANY(%s)
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
