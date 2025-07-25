from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import playwright
import time
import logging
from backend.logs.logger_config import init_logger


# Returns a list of usernames who are sponsoring the user, and a private use count
def scrape_sponsors(username):
    init_logger()

    sponsor_count = 0
    private_sponsors = 0
    user_sponsors = list()
    org_sponsors = list()
    sponsors_list = list()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        url = f"https://github.com/sponsors/{username}"
        page.goto(url)

        if page.url == f"https://github.com/{username}":
            logging.info(f"{username} is not in the sponsors program, 0 sponsors.")
            return [], 0

        # More robust pagination handling
        page_count = 0
        # This limit is set by github (No way to get around pagination limit, disables show more button)
        max_pages = 100
        logging.info(f"Starting Sponsorship Scraping for {username}")

        while page_count < max_pages:
            # Re-query sponsor_div each time to avoid stale element references
            sponsor_div = page.query_selector("#sponsors")
            if not sponsor_div:
                print("Sponsors section not found, stopping")
                break

            # print("Starting Sponsorship Scraping for", username)
            # Wait for content to load
            page.wait_for_timeout(1000)

            # Check if pagination button exists and is clickable
            form = sponsor_div.query_selector(
                "form[data-target='remote-pagination.form']"
            )
            if not form or not form.is_visible():
                print("No pagination form found, stopping")
                break

            button = form.query_selector(
                'button[data-target="remote-pagination.submitButton"]'
            )
            if not button or not button.is_visible() or not button.is_enabled():
                print("No more pages to load")
                break

                # Check if button text indicates "Load more" vs "Loading..."
                # button_text = button.inner_text().lower()
                # if "loading" in button_text:
                #     print("Button is loading, waiting...")
            page.wait_for_timeout(1000)
            #     continue

            print(f"Loading page {page_count + 1}...")

            remote_page_div = sponsor_div.query_selector(
                "div[data-target='remote-pagination.list']"
            )
            if remote_page_div:
                old_count = len(remote_page_div.query_selector_all("div.d-flex"))
                if old_count:
                    print("count of users?", old_count)

            button.click()

            # Wait for new content to load
            for i in range(10):
                page.wait_for_timeout(500)
                # Re-query sponsor_div after page change
                updated_sponsor_div = page.query_selector("#sponsors")
                if updated_sponsor_div:
                    new_count = len(
                        updated_sponsor_div.query_selector_all("a.d-inline-block")
                    )
                    if new_count > old_count:
                        break
            else:
                print("No new content loaded, stopping")
                break

            page_count += 1

        # Final collection - re-query one last time
        final_sponsor_div = page.query_selector("#sponsors")
        if final_sponsor_div:
            private_sponsors = len(
                final_sponsor_div.query_selector_all(
                    "svg[aria-label='Private Sponsor']"
                )
            )
            user_links = final_sponsor_div.query_selector_all(
                "a[data-hovercard-type='user']"
            )
            org_links = final_sponsor_div.query_selector_all(
                "a[data-hovercard-type='organization']"
            )

            print(
                f"Final counts - Private: {private_sponsors}, Users: {len(user_links)}, Orgs: {len(org_links)}"
            )

            # Collect usernames
            for sponsor in org_links:
                href = sponsor.get_attribute("href")
                if href:
                    sponsor_name = href.strip("/").split("/")[-1]
                    org_sponsors.append(sponsor_name)

            for sponsor in user_links:
                href = sponsor.get_attribute("href")
                if href:
                    sponsor_name = href.strip("/").split("/")[-1]
                    user_sponsors.append(sponsor_name)

        page.wait_for_timeout(10000)
        browser.close()

        sponsors_list = user_sponsors + org_sponsors
        total_count = len(sponsors_list) + private_sponsors

        logging.info(
            f"Total Sponsors: {total_count}, Public: {len(sponsors_list)}, Private: {private_sponsors}"
        )
        logging.info(
            f"# of Total Sponsors: {len(sponsors_list) + private_sponsors}, Crosscheck Link: {url}"
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


scrape_sponsors("evcc-io")
