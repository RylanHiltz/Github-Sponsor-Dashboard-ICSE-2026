from backend.db.queries.users import batchGetUserId

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
    print("Created Sponsor Relationships")
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
    print("Created Sponsoring Relationships")
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
    return
