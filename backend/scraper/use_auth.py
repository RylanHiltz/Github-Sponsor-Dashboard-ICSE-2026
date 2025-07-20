from playwright.sync_api import sync_playwright
import os
import time
import json
from dotenv import load_dotenv

# Load login credentials for github auth while scraping
load_dotenv()
USERNAME = os.getenv("gh_username")
PASSWORD = os.getenv("gh_password")


def is_auth_expiring_soon(auth_path="auth.json", hours=24):

    print(f"Checking if auth is expiring soon for: {auth_path}")
    if not os.path.exists(auth_path):
        print("auth.json does not exist.")
        return True
    with open(auth_path) as f:
        data = json.load(f)
    expiries = [
        cookie["expires"]
        for cookie in data.get("cookies", [])
        if cookie.get("expires", -1) > 0
    ]
    if not expiries:
        print("No valid expiry timestamps found.")
        return True
    soonest_expiry = min(expiries)
    expires_in = soonest_expiry - time.time()
    print(f"Soonest expiry: {soonest_expiry} (in {expires_in/3600:.2f} hours)")
    is_expiring = expires_in < hours * 3600
    print(f"Is expiring within {hours} hours? {is_expiring}")
    return is_expiring


def is_auth_valid(auth_path="auth.json"):
    if not os.path.exists(auth_path):
        return False
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=auth_path)
        page = context.new_page()
        page.goto("https://github.com")
        # Check for a logged-in element
        logged_in = page.locator("text=Sign out").is_visible()
        browser.close()
        return logged_in


def get_auth(auth_path="auth.json"):

    if not is_auth_valid(auth_path):
        print("Auth needs to be recreated.")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto("https://github.com/login")

            page.locator('input[name="login"]').fill(USERNAME)
            page.locator('input[name="password"]').fill(PASSWORD)
            page.locator('input[type="submit"]').click()

            context.storage_state(path=auth_path)
            browser.close()
        print("Auth recreated and saved.")
    else:
        print("Auth is valid.")
