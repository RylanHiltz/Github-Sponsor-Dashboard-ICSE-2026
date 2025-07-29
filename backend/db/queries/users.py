# Database imports
from backend.models.github_user import UserModel
from dotenv import load_dotenv
import os
import requests
import json
from openai import OpenAI

# Scraper imports
from playwright.sync_api import sync_playwright

from backend.utils.github_api import getRequest

from backend.db.queries.queue import deleteFromQueue

from datetime import datetime, timezone
import logging
import re

# Load sensitive variables
load_dotenv()
GITHUB_TOKEN = os.getenv("PAT")
EMAIL = os.getenv("email")
API_KEY = os.getenv("API_KEY")


# File for query logic that will be used/imported into the scraper
def createUser(username, db):

    user = getUserData(username, db)

    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (
                github_id,
                username,
                name,
                type,
                has_pronouns,
                gender,
                location,
                avatar_url,
                profile_url,
                company,
                following,
                followers,
                hireable,
                bio,
                public_repos,
                public_gists,
                twitter_username,
                email,
                last_scraped,
                is_enriched,
                github_created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING;
            """,
            (
                user.github_id,
                user.username,
                user.name,
                user.type,
                user.has_pronouns,
                user.gender,
                user.location,
                user.avatar_url,
                user.profile_url,
                user.company,
                user.following,
                user.followers,
                user.hireable,
                user.bio,
                user.public_repos,
                user.public_gists,
                user.twitter_username,
                user.email,
                user.last_scraped,
                user.is_enriched,
                user.github_created_at,
            ),
        )
        # Get the user id
        cur.execute(
            """
            SELECT id FROM users WHERE username = %s;
            """,
            (username,),
        )
        user_id = cur.fetchone()[0]

        db.commit()
        cur.close()
        logging.info(f"Created user: {username}")
    # Returns the user object and user id to the worker
    return user, user_id


# User already exists from previous sponsorship relation, run Github API request, collect and update user data
def enrichUser(username, db, enriched=False, identity=None):

    if not enriched:
        user = getUserData(username, db)
    else:
        user = getUserData(username, db, enriched, identity)

    with db.cursor() as cur:
        cur.execute(
            """
            UPDATE users SET
                github_id = %s,
                name = %s,
                type = %s,
                has_pronouns = %s,
                gender = %s,
                location = %s,
                avatar_url = %s,
                profile_url = %s,
                company = %s,
                following = %s,
                followers = %s,
                hireable = %s,
                bio = %s,
                public_repos = %s,
                public_gists = %s,
                twitter_username = %s,
                email = %s,
                last_scraped = %s,
                is_enriched = %s,
                github_created_at = %s
            WHERE username = %s
            """,
            (
                user.github_id,
                user.name,
                user.type,
                user.has_pronouns,
                user.gender,
                user.location,
                user.avatar_url,
                user.profile_url,
                user.company,
                user.following,
                user.followers,
                user.hireable,
                user.bio,
                user.public_repos,
                user.public_gists,
                user.twitter_username,
                user.email,
                user.last_scraped,
                user.is_enriched,
                user.github_created_at,
                user.username,
            ),
        )
        db.commit()
        cur.close()
        logging.info(f"Enriched user: {username}")
    # Returns the type of the user after getting metadata for scraping
    return user


# Batch create minimum users for sponsorship relations
def batchCreateUser(usernames, db):

    entries = [(username,) for username in usernames]

    with db.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO users (username)
            VALUES (%s)
            ON CONFLICT (username) DO NOTHING;
            """,
            entries,
        )
    db.commit()
    cur.close()
    return


# ! REFACTOR WITH ANOTHER CASE WHERE is_enriched IS FALSE AND TRUE TO MAKE SURE GENDER IS NOT REIMAGINED
def getUserData(username, db, is_enriched=False, identity=None):
    # from backend.db.queries.sponsors import notFoundWithSponsors

    # Call Github REST API to get the metadata for user
    url = f"https://api.github.com/users/{username}"

    try:
        res = getRequest(url)
        data = res.json()
        user = UserModel.from_api(data)

        if user.location != None:
            user.location = getLocation(user.location)

        # If user type is User
        if user.type == "User":
            if not is_enriched:
                user.has_pronouns, user.gender = scrapePronouns(user.username)
                # If user does not have pronouns, infer gender based on name and country
                if not user.has_pronouns:
                    user.gender = getGender(user.name, user.location)
                user.is_enriched = True
                return user
            else:
                # Data that should not be reset when refreshing data
                user.gender = identity["gender"]
                user.has_pronouns = identity["has_pronouns"]
                user.is_enriched = is_enriched
                return user
        # Else user type is Organization
        else:
            user.is_enriched = True
            return user

    # User in DB does not match user in Github (this means the user has changed their username) remove the user & cascade
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logging.error(
                f"{username} has changed usernames or no longer exists on github, Nuke user from DB."
            )
            deleteUser(username, db)
            deleteFromQueue(username, db)
            raise ValueError(f"User {username} not found on GitHub.")
        else:
            logging.error(
                f"Failed to fetch GitHub profile for {username}: {e.response.status_code} {e.response.text}"
            )
            return None


# Attempts to remove words that may confuse the location API to pull country of origin for user
def clean_location(location):
    if not location or location.strip() == "":
        return None

    # Remove common symbols and meaningless characters
    location = re.sub(r'[#@$%^&*()_+=\[\]{}|\\:";\'<>?/~`]', "", location)

    # Remove URLs and email-like patterns
    location = re.sub(r"https?://\S+", "", location)
    location = re.sub(r"\S+@\S+\.\S+", "", location)

    # Remove numbers at the start/end (like zip codes, but keep numbers in middle)
    location = re.sub(r"^\d+\s*|\s*\d+$", "", location)

    # Existing patterns
    patterns_to_remove = [
        r"greater\s+",
        r"area",
        r"metro",
        r"vicinity",
        r"region",
        r"\bthe\b",
    ]

    location = location.lower()
    for pattern in patterns_to_remove:
        location = re.sub(pattern, "", location)

    # Remove extra spaces, commas, and trim
    location = re.sub(r"\s+", " ", location).strip(" ,.-")

    # If location is too short or meaningless after cleaning, return None
    if len(location) < 2 or location.lower() in ["n/a", "none", "null", ""]:
        return None

    return location.title()


def get_most_important_location(locations):
    if not locations:
        return None
    best = max(locations, key=lambda x: x.get("importance", 0))
    address = best.get("address", {})
    return address.get("country")


# Take the location of the github user, use openstreetmap API to pull the country of origin
def getLocation(location):
    location = clean_location(location)
    if location:
        url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&addressdetails=1"
        headers = {
            "User-Agent": f"github-sponsor-dashboard/1.0 ({EMAIL})",
            "Accept-Language": "en",
        }
        res = requests.get(url=url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            if data and "address" in data[0] and "country" in data[0]["address"]:
                country = get_most_important_location(data)
                return country
            else:
                # print(f"No location data found for '{location}'.")
                logging.warning(f"No location data found for '{location}'.")
                return None
        else:
            logging.error(
                f"OpenStreetMap.Org Request failed:", res.status_code, res.text
            )
            return None
    return None


# Scrapes the pronouns of a passed in user
def scrapePronouns(name):
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = f"https://github.com/{name}"

        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()
        page.goto(url)

        # content = page.content()
        pronoun_span = page.query_selector("span[itemprop='pronouns']")
        if pronoun_span:
            pronouns = pronoun_span.inner_text()
            has_pronouns, gender = extract_pronouns(pronouns)
        else:
            has_pronouns, gender = False, None

        browser.close()
        return has_pronouns, gender


# Extracts the pronouns out of the pronoun span (users may have random words and pronouns mixed)
def extract_pronouns(text):
    text = text.lower()

    # Normalize slashes and spaces
    text = re.sub(r"\s*/\s*", "/", text)  # 'he / him' → 'he/him'
    text = re.sub(r"[^\w/]", " ", text)  # remove punctuation except slash

    # Tokenize and look for pronoun sets
    pronouns = re.findall(
        r"\b(?:he/him|she/her|they/them|he/they|she/they|he/her|she/him)\b", text
    )

    if not pronouns:
        return False, None

    found = pronouns[0]

    # Check for ambiguous/mixed combinations
    if found in ["he/her", "she/him"]:
        return True, "Other"

    if found == "he/him" or found == "he/they":
        return True, "Male"
    if found == "she/her" or found == "she/they":
        return True, "Female"
    if found == "they/them":
        return True, "Other"

    # Fallback
    return True, "Other"


# Infer the gender of the username using the full name and current country (assuming place of origin for some users)
def getGender(name, country):
    # Use gpt-4o-mini for gender inferencing
    client = OpenAI(api_key=API_KEY)
    user_message = f"full name: {name}"
    if country is not None:
        user_message += f", current location: {country}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                    Infer gender using fullname. Only output valid json in this format (Try not to output Unknown): { "gender": "Male" }, { "gender": "Female" }, or { "gender": "Unknown" }
                """,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
    )
    output = res.choices[0].message.content
    user = json.loads(output)
    gender = user["gender"]
    return gender


# Runs a check if the user exists in the database an has already been visisted once
def findUser(username, db):
    with db.cursor() as cur:
        cur.execute(
            "SELECT id, is_enriched FROM users WHERE username = %s LIMIT 1;",
            (username,),
        )
        row = cur.fetchone()
        print(row)
        if row:
            user_id = row[0]
            enriched = row[1]

            if enriched:
                # User has been enriched, fetch gender data
                # - Makes sure not to infer gender more than once
                cur.execute(
                    """
                    SELECT
                        gender,
                        has_pronouns
                    FROM users WHERE username = %s LIMIT 1;
                    """,
                    (username,),
                )
                row = cur.fetchone()
                gender = row[0]
                pronouns = row[1]
                cur.close()
                return True, True, user_id, {"gender": gender, "has_pronouns": pronouns}
            else:
                return True, False, user_id, None
        else:
            return False, False, None, None


# Returns an array of user id's mapped to the specific usernames
def batchGetUserId(user_arr, db):

    with db.cursor() as cur:
        query = """
            SELECT id, username 
            FROM users 
            WHERE username = ANY(%s)
        """
        cur.execute(query, (user_arr,))
        rows = cur.fetchall()
        # Convert to a dict or list as needed
        return [id for id, username in rows]
    return


# Deletes a specfic user from the DB
def deleteUser(user, db):
    with db.cursor() as cur:
        cur.execute(
            """
            DELETE FROM users
            WHERE username = %s;
            """,
            (user,),
        )
        db.commit()
        cur.close()
        logging.info(f"Deleted {user} From Database")
        return


# Update last_scraped for the passed in user in the DB
def finalizeUserScrape(username, private_count, min_sponsor_tier, db):

    scraped = datetime.now(timezone.utc)

    with db.cursor() as cur:
        cur.execute(
            """
            UPDATE users SET
                last_scraped = %s,
                private_sponsor_count = %s,
                min_sponsor_cost = %s     
            WHERE username = %s;
            """,
            (scraped, private_count, min_sponsor_tier, username),
        )
        db.commit()
        cur.close()
    return
