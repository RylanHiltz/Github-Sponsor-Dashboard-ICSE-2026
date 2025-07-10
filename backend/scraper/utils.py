from playwright.sync_api import sync_playwright
import playwright
import time


# Returns a list of usernames who are sponsoring the user, and a private use count
def scrape_sponsors(username):
    with sync_playwright() as p:
        sponsors = []
        sponsor_count = 0
        private_sponsors = 0

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = f"https://github.com/sponsors/{username}"
        page.goto(url)

        if page.url == f"https://github.com/{username}":
            print(f"{username} is not in the sponsors program.")
            return []

        while True:
            show_more_clicked = False
            forms = page.query_selector_all(
                f'form[action^="/sponsors/{username}/sponsors_partial?filter=active"]'
            )
            # Only click the first visible form's button
            for form in forms:
                if form.is_visible():
                    button = form.query_selector('button[type="submit"]')
                    if button and button.is_visible():
                        button.click()
                        show_more_clicked = True
                        page.wait_for_timeout(500)
                        break  # Only click one button per loop
            if not show_more_clicked:
                break

        # Get total sponsor count for user
        counter_span = page.query_selector("span.Counter")
        if counter_span:
            sponsor_count = int(counter_span.inner_text())
        else:
            print("Sponsor count span not found.")

        sponsor_div = page.query_selector("#sponsors")
        sponsors = set()
        if sponsor_div:
            user_sponsors = sponsor_div.query_selector_all(
                "a[data-hovercard-type='user']"
            )
            org_sponsors = sponsor_div.query_selector_all(
                "a[data-hovercard-type='organization']"
            )

        # Collect public user sponsor names
        for sponsor in user_sponsors:
            href = sponsor.get_attribute("href")
            if href:
                sponsor_name = href.strip("/").split("/")[-1]
                sponsors.add(sponsor_name)

        # Collect public organization sponsor names
        for sponsor in org_sponsors:
            href = sponsor.get_attribute("href")
            if href:
                sponsor_name = href.strip("/").split("/")[-1]
                sponsors.add(sponsor_name)

        browser.close()
        sponsors_list = list(sponsors)

        # If the sponsor count was able to be extracted, calculate private sponsors
        if sponsor_count:
            private_sponsors = sponsor_count - len(sponsors_list)

        print(sponsors_list)
        print("Number of private sponsors: ", private_sponsors)
        print("number of sponsors: ", len(sponsors_list))
        return sponsors_list, private_sponsors


# Returns a list of usernames who are bering sponsored by the passed in user
def scrape_sponsoring(username, type):

    #
    if type == "user":
        return
    if type == "organization":
        return

    return


scrape_sponsors("yyx990803")
