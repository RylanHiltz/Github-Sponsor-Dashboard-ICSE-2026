# Batch create a sponsored relations for a specific user
def createSponsors(sponsored, sponsor_arr, db):
    entries = [(sponsor, sponsored) for sponsor in sponsor_arr]
    print("ENTRIES:", entries)

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
    print("ENTRIES:", entries)

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
