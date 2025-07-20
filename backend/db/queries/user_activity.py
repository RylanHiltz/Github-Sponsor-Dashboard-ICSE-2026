import requests
from dotenv import load_dotenv
import os
import json

from backend.utils.github_api import api_request

# Load sensitive variables
load_dotenv()
GITHUB_TOKEN = os.getenv("PAT")


# Return the user activity for the passed in user (PR, commits, issues)
def getUserActivity(user, user_id, user_type, db):

    commit_count = getUserRepos(user, user_type)
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
    return


# Returns a list of public repos belonging to the passed in user
def getUserRepos(username, user_type):
    page = 1
    all_repos = []

    # If the user is an Organization, no commits to repos can be made
    if user_type == "Organization":
        return 0

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

    print(len(repos))

    for repo in repos:
        url = f"https://api.github.com/repos/{username}/{repo['name']}/commits?author={username}&per_page=1"
        try:
            _, headers = api_request(url)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:
                print(
                    f"Skipping repo {repo['name']} due to 409 Conflict (Empty Repository.)"
                )
                searched += 1
                continue
            else:
                raise  # re-raise other errors
        link_header = headers.get("link")

        # Increment searched repo count by 1
        searched += 1

        if link_header is None:
            continue
        else:
            links = link_header.split(", ")
            for link in links:
                if 'rel="last"' in link:
                    url = link.split(";")[0].strip("<>")
                    last_link = url
                    count = int(last_link.split("&page=")[-1])
                    commit_count += count
    print(f"All {searched} repos scraped")
    if headers:
        print("Remaning GitHub Tokens:", headers.get("X-RateLimit-Remaining"))

    return commit_count


# Returns the total pull request count of a passed in user
def getPRCount(username):
    url = f"https://api.github.com/search/issues?q=author:{username}+type:pr"
    data, _ = api_request(url)
    pr_count = data["total_count"]
    return pr_count


# Returns the total issue count for a passed in user
def getIssuesCount(username):
    url = f"https://api.github.com/search/issues?q=author:{username}+type:issue"
    data, _ = api_request(url)
    issues_count = data["total_count"]
    return issues_count
