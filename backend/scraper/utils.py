import time
import logging
from backend.logs.logger_config import init_logger
import os
from dotenv import load_dotenv
from backend.utils.github_api import postRequest

load_dotenv()

# Globals
URL = "https://api.github.com/graphql"


# Parent function to handle both functions running
# Return a list of sponsors, sponsored users, and a count of private sponsors
def get_sponsorships(username, user_type):
    logging.info(f"Starting Sponsorship Fetch via API for {user_type} '{username}'")
    sponsor_list, private_count, lowest_tier_cost = get_sponsors_from_api(
        username, user_type
    )
    sponsored_list = get_sponsored_from_api(username, user_type)
    return sponsor_list, sponsored_list, private_count, lowest_tier_cost


# Returns the sponsors that are associated to the passed in user
def get_sponsors_from_api(username, user_type):
    """
    Fetches all sponsors for a given user or organization using the GitHub GraphQL API.
    :param username: The login name of the user or organization.
    :param user_type: The type of account, either 'user' or 'organization'.
    """
    if user_type.lower() not in ["user", "organization"]:
        raise ValueError("user_type must be 'user' or 'organization'")

    sponsors_list = []
    private_sponsors_count = 0
    lowest_tier_cost = 0
    has_next_page = True
    cursor = None
    response = None

    # Dynamic query template for the Github GraphQL API
    query_template = f"""
    query($login: String!, $cursor: String) {{
      {user_type.lower()}(login: $login) {{
        sponsorshipsAsMaintainer(first: 100, after: $cursor, includePrivate: true) {{
          totalCount
          pageInfo {{
            endCursor
            hasNextPage
          }}
          nodes {{
            privacyLevel
            sponsorEntity {{
              ... on User {{ login }}
              ... on Organization {{ login }}
            }}
          }}
        }}
        sponsorsListing {{
          tiers(first: 20) {{
            nodes {{
              monthlyPriceInCents
              isOneTime
            }}
          }}
        }}
      }}
    }}
    """

    print(f"Starting Sponsors Fetch for {user_type} '{username}'")
    start_time = time.time()

    while has_next_page:
        variables = {"login": username, "cursor": cursor}
        query = {"query": query_template, "variables": variables}

        try:
            response = postRequest(url=URL, json=query)
            data = response.json()
        except Exception as e:
            logging.error(
                f"Permanently failed to fetch sponsors for '{username}' after all retries. Error: {e}"
            )
            break

        if not cursor:
            sponsors_listing = (
                data.get("data", {}).get(user_type.lower(), {}).get("sponsorsListing")
            )
            if sponsors_listing and sponsors_listing.get("tiers"):
                tiers = sponsors_listing["tiers"]["nodes"]
                monthly_prices_in_cents = [
                    tier["monthlyPriceInCents"]
                    for tier in tiers
                    if not tier.get("isOneTime") and "monthlyPriceInCents" in tier
                ]
                if monthly_prices_in_cents:
                    lowest_tier_cost = min(monthly_prices_in_cents) / 100
                    print(
                        f"\nLowest monthly tier for {username}: ${lowest_tier_cost:.2f}"
                    )
            else:
                # If tiers are not public, set to a baseline of $5.00
                print(f"{username} does not have a public sponsors listing or tiers.")
                lowest_tier_cost = 5

        sponsorships = (
            data.get("data", {})
            .get(user_type.lower(), {})
            .get("sponsorshipsAsMaintainer")
        )
        if not sponsorships:
            logging.warning(
                f"Could not retrieve sponsorships for {username}. They may not be in the sponsor program or the user type is wrong."
            )
            break

        if not cursor:  # Only log total on the first page
            total_sponsors = sponsorships.get("totalCount", 0)
            logging.info(f"Total sponsors reported by API: {total_sponsors}")

        for node in sponsorships.get("nodes", []):
            if node.get("privacyLevel") == "PRIVATE":
                private_sponsors_count += 1
            elif node.get("sponsorEntity") and node["sponsorEntity"].get("login"):
                sponsors_list.append(node["sponsorEntity"]["login"])

        page_info = sponsorships.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)
        cursor = page_info.get("endCursor")

    end_time = time.time()
    logging.info(f"\nAPI fetch completed in {end_time - start_time:.2f} seconds.")

    total_count = len(sponsors_list) + private_sponsors_count
    logging.info(
        f"Total Sponsors: {total_count}, Public: {len(sponsors_list)}, Private: {private_sponsors_count}"
    )
    logging.info(
        f"Remaining Github API Tokens: {response.headers.get("X-RateLimit-Remaining")}"
    )
    return sponsors_list, private_sponsors_count, lowest_tier_cost


# Returns an array of users who are sponsored by the passed in user
def get_sponsored_from_api(username, user_type):
    """
    Fetches all sponsored for a given user or organization using the GitHub GraphQL API.
    :param username: The login name of the user or organization.
    :param user_type: The type of account, either 'user' or 'organization'.
    """
    init_logger()

    sponsored_list = []
    has_next_page = True
    cursor = None

    # Dynamic query template for the Github GraphQL API
    query_template = f"""
    query($login: String!, $cursor: String) {{
      {user_type.lower()}(login: $login) {{
      sponsorshipsAsSponsor(first: 100, after: $cursor) {{
        totalCount
        pageInfo {{
        endCursor
        hasNextPage
        }}
        nodes {{
        sponsorable {{
          ... on User {{ login }}
          ... on Organization {{ login }}
        }}
        }}
      }}
      }}
    }}
    """

    start_time = time.time()

    print(f"\nStarting Sponsoring Fetch for {user_type} '{username}'")
    while has_next_page:

        variables = {"login": username, "cursor": cursor}
        query = {"query": query_template, "variables": variables}

        try:
            response = postRequest(url=URL, json=query)
            data = response.json()
        except Exception as e:
            logging.error(
                f"Permanently failed to fetch sponsors for '{username}' after all retries. Error: {e}"
            )
            break

        data = response.json()
        if "errors" in data:
            logging.error(f"GraphQL errors: {data['errors']}")
            break

        sponsored = (
            data.get("data", {}).get(user_type.lower(), {}).get("sponsorshipsAsSponsor")
        )
        if not sponsored:
            logging.warning(
                f"Could not retrieve sponsored users for {username}. They may not be sponsoring any users"
            )
            break

        if not cursor:  # Only log total on the first page
            total_sponsoring = sponsored.get("totalCount", 0)
            logging.info(f"Total sponsored users reported by API: {total_sponsoring}")

        for node in sponsored.get("nodes", []):
            if node.get("sponsorable") and node["sponsorable"].get("login"):
                sponsored_list.append(node["sponsorable"]["login"])

        page_info = sponsored.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)
        cursor = page_info.get("endCursor")

    end_time = time.time()
    logging.info(f"API fetch completed in {end_time - start_time:.2f} seconds.")
    logging.info(
        f"Remaining Github API Tokens: {response.headers.get("X-RateLimit-Remaining")}"
    )
    return sponsored_list
