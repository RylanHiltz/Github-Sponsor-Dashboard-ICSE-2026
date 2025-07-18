# Database imports
from backend.models.github_user import UserModel
from dotenv import load_dotenv
import os
import requests
import json
from openai import OpenAI

# Scraper imports
from playwright.sync_api import sync_playwright

# Load sensitive variables
load_dotenv()
GITHUB_TOKEN = os.getenv("PAT")
EMAIL = os.getenv("email")
API_KEY = os.getenv("API_KEY")


# File for query logic that will be used/imported into the scraper
def createUser(username, db):

    try:
        user = getUserData(username)
    except FileNotFoundError as e:
        print(e)
        deleteUser(username, db)
        return None
    if user is None:
        return None

    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (
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
                last_scraped,
                is_enriched
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING;
            """,
            (
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
                user.last_scraped,
                user.is_enriched,
            ),
        )
        db.commit()
        cur.close()
        print(f"Created user: {user.username}")
    # Returns the user object to the worker
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


def getUserData(username):
    # Call Github REST API to get the metadata for user
    url = f"https://api.github.com/users/{username}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        user = UserModel.from_api(data)

        if user.location != None:
            user.location = getLocation(user.location)

        if user.type == "User":
            user.has_pronouns, user.gender = scrapePronouns(user.username)
            # If user does not have pronouns, infer gender based on name and country
            if not user.has_pronouns:
                user.gender = getGender(user.name, user.location)

        user.is_enriched = True
        print(user)
        return user
    # User in DB does not match user in Github (this means the user has changed their username) remove the user & cascade
    if response.status_code == 404:
        raise FileNotFoundError(
            f"GitHub user '{username}' not found (404). Delete this user from the database."
        )
    else:
        print(
            f"Failed to fetch GitHub profile for {username}: {response.status_code} {response.text}"
        )
        return None


# Take the location of the github user, use openstreetmap API to pull the country of origin
def getLocation(location):
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&addressdetails=1"
    headers = {
        "User-Agent": f"github-sponsor-dashboard/1.0 ({EMAIL})",
        "Accept-Language": "en",
    }
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        country = data[0]["address"]["country"]
        return country
    else:
        print("Request failed:", response.status_code, response.text)
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
            if pronouns:
                pronouns_list = [p.strip() for p in pronouns.split("/")]
                has_pronouns = True
                if any(p.lower() in ["he", "him"] for p in pronouns_list):
                    gender = "Male"
                elif any(p.lower() in ["she", "her"] for p in pronouns_list):
                    gender = "Female"
                elif any(p.lower() in ["they", "them"] for p in pronouns_list):
                    gender = "Other"
                else:
                    gender = "Unknown"
        else:
            gender = None
            has_pronouns = False

        print(has_pronouns, gender)
        browser.close()
        return has_pronouns, gender


# Infer the gender of the username using the full name and current country (assuming place of origin for some users)
def getGender(name, country):
    # Use gpt-4o-mini for gender inferencing
    client = OpenAI(api_key=API_KEY)
    user_message = f"full name: {name}"
    if country is not None:
        user_message += f", current location: {country}"

    response = client.chat.completions.create(
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
    output = response.choices[0].message.content
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
            return True, row[0]
        else:
            return False, None


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

    try:
        user = getUserData(username)
    except FileNotFoundError as e:
        print(e)
        deleteUser(username, db)
        return None
    if user is None:
        return None

    with db.cursor() as cur:
        cur.execute(
            """
            UPDATE users SET
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
                last_scraped = %s,
                is_enriched = %s
            WHERE username = %s
            """,
            (
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
                user.last_scraped,
                user.is_enriched,
                user.username,
            ),
        )
        db.commit()
        cur.close()
        print(f"Enriched user: {user.username}")
    # Returns the type of the user after getting metadata for scraping
    return user


# Deletes a specfic user
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
