from playwright.sync_api import sync_playwright
import os
import time
import json
import logging
from dotenv import load_dotenv

# Load login credentials for github auth while scraping
load_dotenv()
USERNAME = os.getenv("gh_username")
PASSWORD = os.getenv("gh_password")

# File pathname of authentication file
AUTH_PATH = "auth.json"


# Checks if the auth file exists, returns True (expiring soon), or time remaining
def is_auth_expiring_soon(auth_path=AUTH_PATH):

    logging.debug(f"Checking if auth is expiring soon for: {auth_path}")
    if not os.path.exists(auth_path):
        logging.debug("auth.json does not exist.")
        return True
    with open(auth_path) as f:
        data = json.load(f)
    expiries = [
        cookie["expires"]
        for cookie in data.get("cookies", [])
        if cookie.get("expires", -1) > 0
    ]
    if not expiries:
        logging.debug("No valid expiry timestamps found.")
        return True
    soonest_expiry = min(expiries)
    expires_in = soonest_expiry - time.time()
    logging.debug(f"Soonest expiry: {soonest_expiry} (in {expires_in/3600:.2f} hours)")
    time_remaining = expires_in < 24 * 3600
    logging.debug(f"Is expiring within 24 hours? {time_remaining}")
    return time_remaining


# Checks if user authentication already exists in browser
def check_auth(auth_path=AUTH_PATH):
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


# Headlessy logs into github using venv account details
def get_auth(auth_path=AUTH_PATH):
    # If Github authentication has expired or doesnt exist
    if check_auth(auth_path) is False:
        print("Auth needs to be recreated.")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto("https://github.com/login")

            # Fill in login info and submit
            page.locator('input[name="login"]').fill(USERNAME)
            page.locator('input[name="password"]').fill(PASSWORD)
            page.locator('input[type="submit"]').click()

            # Store authentication cookies in auth.json
            context.storage_state(path=auth_path)
            browser.close()
        logging.debug("Auth recreated and saved.")
    # Github authentication file is valid/does not need to be created
    else:
        logging.debug("Auth is valid.")
