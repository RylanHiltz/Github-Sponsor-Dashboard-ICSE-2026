import requests
import time
import os
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
            remaining = res.headers.get("X-RateLimit-Remaining")
            reset = res.headers.get("X-RateLimit-Reset")
            # If API request is 0
            if remaining == "0" and reset:
                reset_time = int(reset)
                now = int(time.time())
                sleep_time = reset_time - now
                print(f"[Rate Limit Hit] Sleeping {sleep_time} seconds...")
                time.sleep(sleep_time + 5)
                continue
            else:
                raise Exception(f"403 Forbidden, not due to rate limit: {res.text}")
        else:
            res.raise_for_status()
