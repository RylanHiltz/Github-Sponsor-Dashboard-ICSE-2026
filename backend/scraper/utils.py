from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import playwright
import time
import logging


# Returns a list of usernames who are sponsoring the user, and a private use count
def scrape_sponsors(username):

    sponsor_count = 0  # Count of total sponsors on the page
    private_sponsors = 0  # Private sponsors who do not have accessible Github's
    user_sponsors = list()  # Array of user sponsors
    org_sponsors = list()  # Array of organization sponsors
    sponsors_list = list()
    user_links = []
    org_links = []

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = f"https://github.com/sponsors/{username}"
        page.goto(url)

        if page.url == f"https://github.com/{username}":
            logging.info(f"{username} is not in the sponsors program, 0 sponsors.")
            # These should all be null/empty
            return [], 0

        sponsor_div = page.query_selector("#sponsors")

        # Get total sponsor count for user
        counter_span = page.query_selector("span.Counter")
        if counter_span:
            sponsor_count = int(counter_span.inner_text().replace(",", ""))
        else:
            print("Sponsor count span not found.")

        if sponsor_div:
            print("Starting Sponsorship Scraping for", username)
            form = sponsor_div.query_selector(
                "form[data-target='remote-pagination.form']"
            )
            if form.is_visible():
                button = form.query_selector(
                    'button[data-target="remote-pagination.submitButton"]'
                )
                while True:
                    if button.is_visible() and button.is_enabled():
                        button.click()
                        page.wait_for_timeout(300)  # wait for sponsors to load
                    else:
                        break
            user_links = sponsor_div.query_selector_all("a[data-hovercard-type='user']")
            org_links = sponsor_div.query_selector_all(
                "a[data-hovercard-type='organization']"
            )

        # Collect public organization sponsor names
        if org_links:
            for sponsor in org_links:
                href = sponsor.get_attribute("href")
                if href:
                    sponsor_name = href.strip("/").split("/")[-1]
                    org_sponsors.append(sponsor_name)

        # Collect public user sponsor names
        if user_links:
            for sponsor in user_links:
                href = sponsor.get_attribute("href")
                if href:
                    sponsor_name = href.strip("/").split("/")[-1]
                    user_sponsors.append(sponsor_name)

        browser.close()

        sponsors_list = user_sponsors + org_sponsors
        user_count = len(user_sponsors)
        org_count = len(org_sponsors)

        # If the sponsor count was able to be extracted, calculate private sponsors
        if sponsor_count:
            private_sponsors = sponsor_count - len(sponsors_list)

        logging.info(
            f"# of Total Sponsors: {len(sponsors_list) + private_sponsors}, Crosscheck Link: {url}"
        )
        logging.info(
            f"# of Private Sponsors {private_sponsors}, Users: {user_count}, Orgs: {org_count} (Total [Excluding Private]: {user_count + org_count})"
        )
        return sponsors_list, private_sponsors


# Returns a list of usernames who are being sponsored by the passed in user/org
def scrape_sponsoring(name, type):

    if type == "User":
        sponsoring_list = user_sponsoring(username=name)
    elif type == "Organization":
        sponsoring_list = org_sponsoring(org_name=name)
    else:
        print(f"Unknown type: {type}")
        sponsoring_list = []

    return sponsoring_list


# Scrapes the sponsoring page of the passed in user
def user_sponsoring(username):

    sponsoring_list = list()

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = f"https://github.com/{username}?tab=sponsoring"
        page.goto(url)

        try:
            sponsoring_section = page.wait_for_selector("div.col-lg-12", timeout=4000)
        except PlaywrightTimeoutError as e:
            # Error checking for 404 Not Found (Private user activity)
            image_locator = page.locator(
                'img[src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQ8A…gCtqDfl9vpjt4JrmOra3/B72L99CCrFH3AAAAAElFTkSuQmCC"]'
            )
            if image_locator:
                logging.warning(
                    "This users account is private and cannot be accessed (but is sponsoring other user who have been scraped)"
                )
                return []

        if sponsoring_section:

            button = sponsoring_section.query_selector("a[class='next_page']")

            while True:

                rows = sponsoring_section.query_selector_all("div.color-border-muted")
                for row in rows:
                    past_sponsor = (
                        row.query_selector("span.Label--secondary") is not None
                    )
                    if not past_sponsor:
                        # Avater and user Link are the same component, inner_div handles duplicate
                        inner_div = row.query_selector("div.d-table-cell")
                        if inner_div:
                            user_links = inner_div.query_selector_all(
                                "a[data-hovercard-type='user']"
                            )
                            org_links = inner_div.query_selector_all(
                                "a[data-hovercard-type='organization']"
                            )

                            # Collect sponsored users
                            for sponsored in user_links:
                                href = sponsored.get_attribute("href")
                                if href:
                                    sponsored_name = href.strip("/").split("/")[-1]
                                    sponsoring_list.append(sponsored_name)

                            # Collect sponsored organizations
                            for sponsored in org_links:
                                href = sponsored.get_attribute("href")
                                if href:
                                    sponsored_name = href.strip("/").split("/")[-1]
                                    sponsoring_list.append(sponsored_name)

                # After clicking next, re-query sponsoring_section and button
                button = sponsoring_section.query_selector("a[class='next_page']")

                # if the pagination button exists and is enabled, click and continue scraping
                if button and button.is_visible() and button.is_enabled():
                    button.click()
                    page.wait_for_timeout(750)
                    # Update sponsoring section to load new user data
                    sponsoring_section = page.query_selector("div.col-lg-12")
                else:
                    break
        sponsoring_count = len(sponsoring_list)
        # print(len(sponsoring_list), "Accounts Sponsored, Crosscheck Link: ", url)
        logging.info(f"{sponsoring_count} Accounts Sponsored, Crosscheck Link: {url}")

        browser.close()
        return sponsoring_list


# Scrapes the sponsoring page of the organization
def org_sponsoring(org_name):
    sponsoring_list = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        url = f"https://github.com/orgs/{org_name}/sponsoring"
        page.goto(url)
        time.sleep(1)

        while True:
            # Find the table of sponsors on the current page
            table_body = page.query_selector("tbody.TableBody")
            if table_body:
                rows = table_body.query_selector_all("tr.TableRow")
                for row in rows:
                    link = row.query_selector("a.prc-Link-Link-85e08")
                    if link:
                        href = link.get_attribute("href")
                        if href:
                            user = href.strip("/").split("/")[-1]
                            sponsoring_list.append(user)

            # Find pagination buttons
            buttons = page.query_selector_all("button.TablePaginationAction")
            if buttons:
                next_button = buttons[-1]
                # Check if this is still active ("data-has-page" is true)
                if next_button.get_attribute("data-has-page") == "true":
                    next_button.click()
                    page.wait_for_timeout(300)
                else:
                    break
            else:
                break

        browser.close()
        sponsoring_count = len(sponsoring_list)
        # print(len(sponsoring_list), "Accounts Sponsored, Crosscheck Link: ", url)
        logging.info(f"{sponsoring_count} Accounts Sponsored, Crosscheck Link: {url}")
    return sponsoring_list
