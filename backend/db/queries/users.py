# Database imports
from backend.utils.db_conn import db_connection
from backend.models.github_user import UserModel
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
import os
import requests

# Scraper imports
from playwright.sync_api import sync_playwright
import playwright
import time

# Load Github auth token for API calls
load_dotenv()
GITHUB_TOKEN = os.getenv("PAT")


# File for query logic that will be used/imported into the scraper
def createUser(username):
    # TODO: Calls Github REST API to get the metadata for user
    # cur = db.cursor()
    url = f"https://api.github.com/users/{username}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        user = UserModel.from_api(data)
        user.location = getLocation(user.location)

    print(user)

    # if requests.status_codes == 200:
    #     cur.execute(
    #         """
    #         INSERT
    #         """
    #     )
    # cur.close()
    return


# Take the location of the github user, use openstreetmap API to pull the country of origin
def getLocation(location):
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&addressdetails=1"
    headers = {"User-Agent": "github-sponsor-dashboard/1.0 (rylanhiltz2@gmail.com)"}
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        country = data[0]["address"]["country"]
        return country
    else:
        print("Request failed:", response.status_code, response.text)
        return None


def getGender(username):

    gender = ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = f"https://github.com/{username}"
        page.goto(url)

    return


def findUser(username, db):

    return False


# getLocation("İstanbul")
createUser("DrewAPicture")
