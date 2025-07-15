from playwright.sync_api import sync_playwright
import playwright
import time


# Returns a list of usernames who are sponsoring the user, and a private use count
def scrape_sponsors(username):

    sponsor_count = 0  # Count of total sponsors on the page
    private_sponsors = 0  # Private sponsors who do not have accessible Github's
    user_sponsors = list()  # Array of user sponsors
    org_sponsors = list()  # Array of organization sponsors
    sponsors_list = list()

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = f"https://github.com/sponsors/{username}"
        page.goto(url)

        if page.url == f"https://github.com/{username}":
            print(f"{username} is not in the sponsors program.")
            # These should all be null/empty
            return user_sponsors, org_sponsors, private_sponsors

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
                        page.wait_for_timeout(150)
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

        if sponsor_div:
            user_links = sponsor_div.query_selector_all("a[data-hovercard-type='user']")
            org_links = sponsor_div.query_selector_all(
                "a[data-hovercard-type='organization']"
            )

        # Collect public organization sponsor names
        for sponsor in org_links:
            href = sponsor.get_attribute("href")
            if href:
                sponsor_name = href.strip("/").split("/")[-1]
                org_sponsors.append(sponsor_name)

        # Collect public user sponsor names
        for sponsor in user_links:
            href = sponsor.get_attribute("href")
            if href:
                sponsor_name = href.strip("/").split("/")[-1]
                user_sponsors.append(sponsor_name)

        browser.close()

        sponsors_list = user_sponsors + org_sponsors

        # If the sponsor count was able to be extracted, calculate private sponsors
        if sponsor_count:
            private_sponsors = sponsor_count - len(sponsors_list)

        print("Number of sponsors: ", len(sponsors_list) + private_sponsors)
        print("Private sponsors: ", private_sponsors)
        print("User sponsors: ", len(user_sponsors))
        print("Org sponsors: ", len(org_sponsors))
        return sponsors_list, private_sponsors


# Returns a list of usernames who are being sponsored by the passed in user/org
def scrape_sponsoring(name, type):

    if type == "User":
        sponsoring_arr = user_sponsoring(username=name)
    elif type == "Organization":
        sponsoring_arr = org_sponsoring(org_name=name)
    else:
        print(f"Unknown type: {type}")
        sponsoring_arr = []

    return sponsoring_arr


# Scrapes the sponsoring page of the passed in user
def user_sponsoring(username):

    sponsoring_arr = list()

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = f"https://github.com/{username}?tab=sponsoring"
        page.goto(url)

        sponsoring_section = page.query_selector("div.col-lg-12")

        if sponsoring_section:
            rows = sponsoring_section.query_selector_all("div.color-border-muted")
            for row in rows:
                past_sponsor = row.query_selector("span.Label--secondary") is not None
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
                                sponsoring_arr.append(sponsored_name)

                        # Collect sponsored organizations
                        for sponsored in org_links:
                            href = sponsored.get_attribute("href")
                            if href:
                                sponsored_name = href.strip("/").split("/")[-1]
                                sponsoring_arr.append(sponsored_name)

        browser.close()
        return sponsoring_arr


# Scrapes the sponsoring page of the organization
def org_sponsoring(org_name):

    sponsoring_list = list()

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = f"https://github.com/orgs/{org_name}/sponsoring"
        page.goto(url)

        table_body = page.query_selector("tbody.TableBody")
        if table_body:
            rows = table_body.query_selector_all("tr.TableRow")
            for row in rows:
                link = row.query_selector("a.prc-Link-Link-85e08")
                if link:
                    avatar_img = link.query_selector("img[data-component='Avatar']")
                    if avatar_img:
                        is_org = avatar_img.get_attribute("data-square") is not None
                        href = link.get_attribute("href")
                        if href:
                            user = href.strip("/").split("/")[-1]
                            sponsoring_list.append(user)
        browser.close()
        return sponsoring_list
