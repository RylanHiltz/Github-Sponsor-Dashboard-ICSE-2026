import time
import logging
from backend.logs.logger_config import init_logger
import os
import base64
from dotenv import load_dotenv
from backend.utils.github_api import postRequest
import json

load_dotenv()

# Globals
URL = "https://api.github.com/graphql"


# Parent function to handle both functions running
# Return a list of sponsors, sponsored users, and a count of private sponsors
def get_sponsorships(username, github_id: int, user_type):
    logging.info(f"Starting Sponsorship Fetch via API for {user_type} '{username}'")

    sponsor_list, private_count, lowest_tier_cost = get_sponsors_from_api(
        github_id,
        user_type,
    )
    sponsored_list = get_sponsored_from_api(
        github_id,
        user_type,
    )
    return sponsor_list, sponsored_list, private_count, lowest_tier_cost


# Returns the sponsors that are associated to the passed in user
def get_sponsors_from_api(github_id, user_type):
    """
    Fetches all sponsors for a given user or organization using the GitHub GraphQL API.
        :param username: The login name of the user or organization.
        :param user_type: The type of account, either 'user' or 'organization'.

    If a user does not have a minimum monthly tier, the database will set that value to 0.
    Their monthly income estimate will be derived from the median monthly sponsor cost.
    """
    if user_type.lower() not in ["user", "organization"]:
        raise ValueError("user_type must be 'user' or 'organization'")

    prefix = "04:" if user_type.lower() == "user" else "12:"
    node_id = base64.b64encode(
        f"{prefix}{user_type.title()}{github_id}".encode("utf-8")
    ).decode("utf-8")

    sponsors_list: list[int] = []
    private_sponsors_count = 0
    lowest_tier_cost = 0
    has_next_page = True
    cursor = None
    response = None

    # Dynamic query template for the Github GraphQL API
    query_template = f"""
    query($nodeId: ID!, $cursor: String) {{
      node(id: $nodeId) {{
        ... on {user_type.title()} {{
          sponsorshipsAsMaintainer(first: 100, after: $cursor, includePrivate: true) {{
            totalCount
            pageInfo {{
              endCursor
              hasNextPage
            }}
            nodes {{
              privacyLevel
              sponsorEntity {{
                ... on User {{ databaseId }}
                ... on Organization {{ databaseId }}
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
    }}
    """

    print(f"Starting Sponsors Fetch for {user_type} ''")
    start_time = time.time()

    while has_next_page:
        # Corrected variables dictionary. The key 'nodeId' must match the query variable '$nodeId'.
        variables = {"nodeId": node_id, "cursor": cursor}
        query = {"query": query_template, "variables": variables}

        try:
            response = postRequest(url=URL, json=query)
            data = response.json()
        except Exception as e:
            logging.error(f"Failed to fetch sponsors. Error: {e}")
            break

        if "errors" in data:
            logging.error(f"GraphQL errors: {data['errors']}")
            break

        # The data is now nested inside the 'node' field
        entity_data = data.get("data", {}).get("node", {})
        if not entity_data:
            logging.warning("Could not find entity with the provided ID.")
            break

        if not cursor:  # First page
            sponsors_listing = entity_data.get("sponsorsListing")
            if sponsors_listing and sponsors_listing.get("tiers"):
                tiers = sponsors_listing["tiers"]["nodes"]
                monthly_prices_in_cents = [
                    tier["monthlyPriceInCents"]
                    for tier in tiers
                    if not tier.get("isOneTime") and "monthlyPriceInCents" in tier
                ]
                if monthly_prices_in_cents:
                    lowest_tier_cost = min(monthly_prices_in_cents) / 100
                    logging.info(f"Lowest monthly tier: ${lowest_tier_cost:.2f}")

        sponsorships = entity_data.get("sponsorshipsAsMaintainer")
        if not sponsorships:
            logging.info(f"Could not retrieve sponsorships for ID {github_id}.")
            break

        if not cursor:
            total_sponsors = sponsorships.get("totalCount", 0)
            logging.info(f"Total sponsors reported by API: {total_sponsors}")

        for node in sponsorships.get("nodes", []):
            if not node:
                continue
            if node.get("privacyLevel") == "PRIVATE":
                private_sponsors_count += 1
            elif node.get("sponsorEntity") and node["sponsorEntity"].get("databaseId"):
                sponsors_list.append(node["sponsorEntity"]["databaseId"])

        page_info = sponsorships.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)
        cursor = page_info.get("endCursor")

    end_time = time.time()
    logging.info(f"API fetch completed in {end_time - start_time:.2f} seconds.")
    print(sponsors_list, len(sponsors_list))

    return sponsors_list, private_sponsors_count, lowest_tier_cost


# Returns an array of users who are sponsored by the passed in user
def get_sponsored_from_api(github_id, user_type):
    """
    Fetches all sponsored for a given user or organization using the GitHub GraphQL API.
    :param github_id: The database ID of the user or organization.
    :param user_type: The type of account, either 'user' or 'organization'.
    """
    if user_type.lower() not in ["user", "organization"]:
        raise ValueError("user_type must be 'user' or 'organization'")

    # The prefix for a User ID is '04:' and for an Organization ID is '12:'.
    # This is not officially documented but is the current standard.
    prefix = "04:" if user_type.lower() == "user" else "12:"
    node_id = base64.b64encode(
        f"{prefix}{user_type.title()}{github_id}".encode("utf-8")
    ).decode("utf-8")

    sponsored_list: list[int] = []
    has_next_page = True
    cursor = None

    # Dynamic query template for the Github GraphQL API
    query_template = f"""
    query($nodeId: ID!, $cursor: String) {{
      node(id: $nodeId) {{
        ... on {user_type.title()} {{
          sponsorshipsAsSponsor(first: 100, after: $cursor) {{
            totalCount
            pageInfo {{
              endCursor
              hasNextPage
            }}
            nodes {{
              sponsorable {{
                ... on User {{ databaseId }}
                ... on Organization {{ databaseId }}
              }}
            }}
          }}
        }}
      }}
    }}
    """

    start_time = time.time()

    logging.info(f"Starting Sponsoring Fetch for {user_type} ID '{github_id}'")
    while has_next_page:
        variables = {"nodeId": node_id, "cursor": cursor}
        query = {"query": query_template, "variables": variables}

        try:
            response = postRequest(url=URL, json=query)
            data = response.json()
        except Exception as e:
            logging.error(
                f"Permanently failed to fetch sponsored for ID '{github_id}' after all retries. Error: {e}"
            )
            break

        if "errors" in data:
            logging.error(f"GraphQL errors: {data['errors']}")
            break

        entity_data = data.get("data", {}).get("node", {})
        if not entity_data:
            logging.warning(f"Could not find entity with the provided ID {github_id}.")
            break

        sponsored = entity_data.get("sponsorshipsAsSponsor")
        if not sponsored:
            logging.warning(
                f"Could not retrieve sponsored users for ID {github_id}. They may not be sponsoring any users."
            )
            break

        if not cursor:  # Only log total on the first page
            total_sponsoring = sponsored.get("totalCount", 0)
            logging.info(f"Total sponsored users reported by API: {total_sponsoring}")

        for node in sponsored.get("nodes", []):
            if (
                node
                and node.get("sponsorable")
                and node["sponsorable"].get("databaseId")
            ):
                sponsored_list.append(node["sponsorable"]["databaseId"])

        page_info = sponsored.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)
        cursor = page_info.get("endCursor")

    end_time = time.time()
    logging.info(f"API fetch completed in {end_time - start_time:.2f} seconds.")
    if response:
        logging.info(
            f"Remaining Github API Tokens: {response.headers.get('X-RateLimit-Remaining')}"
        )
    print(sponsored_list, len(sponsored_list))
    return sponsored_list
