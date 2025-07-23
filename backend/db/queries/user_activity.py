import requests
from dotenv import load_dotenv
import os
import json
import logging
import time

from backend.utils.github_api import api_request
from backend.logs.logger_config import log_section

# Load sensitive variables
load_dotenv()
GITHUB_TOKEN = os.getenv("PAT")
HTTPS_MESSAGES = {
    404: "Not Found: The requested resource does not exist. This may occur if the repository or user does not exist.",
    409: "Conflict: The repository is empty or there is a conflict preventing the request from being processed.",
    422: "Unprocessable Entity: The request was well-formed but could not be followed due to semantic errors (e.g., lack of permissions or invalid parameters).",
    451: "Unavailable For Legal Reasons: The resource is not available due to legal reasons (e.g., DMCA takedown).",
    500: "Internal Server Error: GitHub encountered an unexpected condition that prevented it from fulfilling the request.",
    502: "Bad Gateway: GitHub is down or being upgraded. The server received an invalid response from the upstream server.",
    504: "Gateway Timeout: The server did not receive a timely response from the upstream server.",
}


# Return the user activity for the passed in user (PR, commits, issues)
def getUserActivity(user, user_id, user_type, db):

    start = int(time.time())

    # If the user is type org, the account cannot have any of the specified user activities
    if user_type == "Organization":
        commit_count = 0
        pr_count = 0
        issues_count = 0
    else:
        log_section(f"Collecting User Activity Data For: {user}")
        commit_count = getUserRepos(user)
        pr_count = getPRCount(user)
        issues_count = getIssuesCount(user)

    print(
        "commits:",
        commit_count,
        ", pull requests:",
        pr_count,
        ", issues:",
        issues_count,
    )
    logging.info(
        f"DONE: Commits: {commit_count}, PR Count: {pr_count}, Issues Count: {issues_count}"
    )

    if (commit_count, pr_count, issues_count):
        with db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO user_activity (
                user_id,
                commit_count,
                pr_count,
                issues_count
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING;
            """,
                (user_id, commit_count, pr_count, issues_count),
            )
        db.commit()
        cur.close()

    end = int(time.time())
    elapsed = end - start
    logging.info(f"User Activity Data Collected: Elapsed {elapsed:.2f}")

    return


# Returns a list of public repos belonging to the passed in user
def getUserRepos(username):
    page = 1
    all_repos = []

    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
        data, _ = api_request(url)

        # If page has 0 repos, break
        if not data:
            break

        all_repos.extend(data)

        # If page has less than 100 enteries? (last page in api request)
        if len(data) < 100:
            break
        page += 1
    # If repos exist, get the commit count, else return 0
    if all_repos:
        commits = getCommitCount(username=username, repos=all_repos)
        return commits
    return 0


# For the passed in repository, return the number of public commits belonging to the user
def getCommitCount(username, repos):
    commit_count = 0
    searched = 0

    print(f"Checking {len(repos)} Repositories for {username}:")

    for repo in repos:
        url = f"https://api.github.com/repos/{username}/{repo['name']}/commits?author={username}&per_page=1"
        try:
            _, headers = api_request(url)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in HTTPS_MESSAGES:
                logging.warning(
                    f"{e.response.status_code}: {HTTPS_MESSAGES[e.response.status_code]}"
                )
            else:
                raise  # re-raise other errors
            searched += 1
            print(
                f"\rChecking repositories: {searched}/{len(repos)}",
                end="",
                flush=True,
            )
            continue
        link_header = headers.get("link")

        # Increment searched repo count by 1
        searched += 1

        if link_header is None:
            print(
                f"\rChecking repositories: {searched}/{len(repos)}",
                end="",
                flush=True,
            )
            continue
        else:
            links = link_header.split(", ")
            for link in links:
                if 'rel="last"' in link:
                    url = link.split(";")[0].strip("<>")
                    last_link = url
                    count = int(last_link.split("&page=")[-1])
                    commit_count += count
                    print(
                        f"\rChecking repositories: {searched}/{len(repos)}",
                        end="",
                        flush=True,
                    )
    print(f"\nAll {searched} repos scraped")
    if headers:
        tokens = headers.get("X-RateLimit-Remaining")
        print(f"Remaining GitHub Tokens: {tokens}")
        logging.info(f"Remaining GitHub Tokens: {tokens}")
    return commit_count


# Returns the total pull request count of a passed in user
def getPRCount(username):
    url = f"https://api.github.com/search/issues?q=author:{username}+type:pr"
    try:
        data, _ = api_request(url)
        pr_count = data["total_count"]
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            logging.warning(
                f"{e.response.status_code}: Setting PR Count to 0, Unprocessable Entity for URL (Lack Permissions to View User)"
            )
            pr_count = 0
    return pr_count


# Returns the total issue count for a passed in user
def getIssuesCount(username):
    url = f"https://api.github.com/search/issues?q=author:{username}+type:issue"
    try:
        data, _ = api_request(url)
        issues_count = data["total_count"]
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            logging.warning(
                f"{e.response.status_code}: Setting Issues Count to 0, Unprocessable Entity for URL (Lack Permissions to View User)"
            )
            issues_count = 0
    return issues_count
