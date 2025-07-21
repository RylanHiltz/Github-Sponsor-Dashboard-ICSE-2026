# Database imports
from backend.models.github_user import UserModel
from dotenv import load_dotenv
import os
import requests
import json
from openai import OpenAI

# Scraper imports
from playwright.sync_api import sync_playwright

from backend.utils.github_api import api_request

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
                is_enriched
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            ),
        )
        # Get the user id
        cur.execute(
            """
            SELECT id FROM users WHERE username = %s;
            """,
            (user.username,),
        )
        user_id = cur.fetchone()[0]

        db.commit()
        cur.close()
        print(f"Created user: {user.username}")
    # Returns the user object to the worker
    return user, user_id


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


def getUserData(username, db):
    # Call Github REST API to get the metadata for user
    url = f"https://api.github.com/users/{username}"

    try:
        data, _ = api_request(url)  # <-- unpack both
        user = UserModel.from_api(data)

        if user.location != None:
            user.location = getLocation(user.location)

        # If user type is User
        if user.type == "User":
            user.has_pronouns, user.gender = scrapePronouns(user.username)
            # If user does not have pronouns, infer gender based on name and country
            if not user.has_pronouns:
                user.gender = getGender(user.name, user.location)
            user.is_enriched = True
            print(user)
            return user
        # Else user type is Organization
        else:
            user.is_enriched = True
            print(user)
            return user
    # User in DB does not match user in Github (this means the user has changed their username) remove the user & cascade
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logging.error(
                f"{username} has changed usernames or no longer exists on github, Nuke user from DB."
            )
            deleteUser(username, db)
            deleteFromQueue(username, db)
        else:
            logging.error(
                f"Failed to fetch GitHub profile for {username}: {e.response.status_code} {e.response.text}"
            )
            return None


# Attempts to remove words that may confuse the location API to pull country of origin for user
def clean_location(location):
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
    # Remove extra spaces, commas
    location = re.sub(r"\s+", " ", location).strip(" ,")
    print("Cleaned location for API:", location.title())
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
            print(f"No location data found for '{location}'.")
            return None
    else:
        logging.error(f"OpenStreetMap.Org Request failed:", res.status_code, res.text)
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
    # Normalize casing
    text = text.lower()

    # Regex pattern to catch common pronouns, regardless of surrounding text
    pronoun_patterns = [r"\bhe/?him\b", r"\bshe/?her\b", r"\bthey/?them\b"]

    for pattern in pronoun_patterns:
        if re.search(pattern, text):
            # Attempt to catch mixed pronouns, return gender Other if so
            if ("he" in pattern and "her" in pattern) or (
                "she" in pattern and "him" in pattern
            ):
                return True, "Other"
            if "he" in pattern or "him" in pattern:
                return True, "Male"
            elif "she" in pattern or "her" in pattern:
                return True, "Female"
            elif "they" in pattern or "them" in pattern:
                return True, "Other"
    return False, None


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


# Check if the passed in username exists in the DB
def findUser(username, db):
    with db.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s LIMIT 1;", (username,))
        row = cur.fetchone()
        cur.close()
        if row:
            return True
        else:
            return False


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


# User already exists from previous sponsorship relation, run Github API request, collect and update user data
def enrichUser(username, db):

    user = getUserData(username, db)

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
                is_enriched = %s
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
                user.username,
            ),
        )
        # Get the user id
        cur.execute(
            """
            SELECT id FROM users WHERE username = %s;
            """,
            (user.username,),
        )
        user_id = cur.fetchone()[0]

        db.commit()
        cur.close()
        print(f"Enriched user: {user.username}")
    # Returns the type of the user after getting metadata for scraping
    return user, user_id


# Deletes a specfic user from the DB
def deleteUser(user, db):
    with db.cursor() as cur:
        cur.execute(
            """
            DELETE FROM users
            WHERE username = %s;
            """,
            (user),
        )
        db.commit()
        cur.close()
        print(f"Deleted {user}")
        return


# Update final remaining data attributes at the end of worker
def finalizeUserScrape(username, private_count, db):
    updateScraped(username, db)
    updatePrivate(username, private_count, db)


# Update last_scraped for the passed in user in the DB
def updateScraped(username, db):

    scraped = datetime.now(timezone.utc)

    with db.cursor() as cur:
        cur.execute(
            """
            UPDATE users SET
                last_scraped = %s            
            WHERE username = %s;
            """,
            (scraped, username),
        )
        db.commit()
        cur.close()
    return


# Update the private_sponsor_count for the passed in user in the DB
def updatePrivate(username, private_count, db):

    with db.cursor() as cur:
        cur.execute(
            """
            UPDATE users SET
                private_sponsor_count = %s            
            WHERE username = %s;
            """,
            (private_count, username),
        )
        db.commit()
        cur.close()
    return
