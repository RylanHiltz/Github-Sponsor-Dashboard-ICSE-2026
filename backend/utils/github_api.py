import requests
import time
import os
import logging
from dotenv import load_dotenv


load_dotenv()
GITHUB_TOKEN = os.getenv("PAT")


# Function for managing github REST API calls and checking for exceeded limits
def api_request(url):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    while True:
        res = requests.get(url=url, headers=headers)

        if res.status_code == 200:
            return res.json(), res.headers
        elif res.status_code == 403:
            if "Repository access blocked" in res.text:
                logging.warning(
                    f"{res.status_code}: Repository access blocked, Skipping. {url}"
                )
                return [], {}  # Return empty data so scraper can continue
            remaining = res.headers.get("X-RateLimit-Remaining")
            reset = res.headers.get("X-RateLimit-Reset")
            # If API request tokens remaining hits 0
            if remaining == "0" and reset:
                reset_time = int(reset)
                now = int(time.time())
                sleep_time = reset_time - now
                print(f"\n\n[Rate Limit Hit] Sleeping {sleep_time} seconds...")
                for i in range(sleep_time + 5):
                    print(f"\rCurrent Time Slept: {i} seconds", end="", flush=True)
                    time.sleep(1)
                print("\nGithub Tokens Restored!\n\n")
                continue
            else:
                logging.error(f"{res.status_code}: API ERROR: {res.text}")
                raise Exception(f"403 Forbidden, not due to rate limit: {res.text}")
        else:
            res.raise_for_status()
