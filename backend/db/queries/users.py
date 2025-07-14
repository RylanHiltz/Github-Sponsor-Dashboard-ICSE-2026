# Database imports
from backend.models.github_user import UserModel
from dotenv import load_dotenv
import os
import requests
import json
from openai import OpenAI


# Load Github auth token for API calls
load_dotenv()
GITHUB_TOKEN = os.getenv("PAT")
EMAIL = os.getenv("email")
API_KEY = os.getenv("API_KEY")


# File for query logic that will be used/imported into the scraper
def createUser(username, db):

    user = getUserData(username)
    if user is None:
        return None

    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (
                username,
                name,
                type,
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING;
            """,
            (
                user.username,
                user.name,
                user.type,
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
        print(f"Inserted user {user.username}")
        return True


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
        print(data)
        country = data[0]["address"]["country"]
        return country
    else:
        print("Request failed:", response.status_code, response.text)
        return None


# Infer the gender of the username using the full name and current country (assuming place of origin for some users)
def getGender(name, country):
    # Use gpt-4o-mini for gender inferencing
    client = OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": """
                    Infer gender using full name & current location. Only output valid json in this format: { "gender": "Male" }, { "gender": "Female" }, or { "gender": "Unknown" }
                """,
            },
            {
                "role": "user",
                "content": f"full name: {name}, current location: {country}",
            },
        ],
    )
    output = response.choices[0].message.content
    user = json.loads(output)
    gender = user["gender"]
    return gender


def findUser(username, db):

    return False


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
        print(f"Updated user {user.username}")
        return True


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


# getLocation("İstanbul")
# createUser("yyx990803")
# getGender("Rylan Hiltz", "Canada")
# getUserData("sakura-ryoko")
