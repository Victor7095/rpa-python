from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems

browser_lib = Selenium()


def open_the_website(url):
    browser_lib.open_available_browser(
        url, options={"arguments": ["window-size=1920,1080"]})


def click_agree_with_terms():
    browser_lib.wait_until_page_contains_element(
        "css:div#complianceOverlay")
    click_button("css:div#complianceOverlay button[type='button']")


def click_search_button():
    button_locator = "css:button[data-testid='search-button']"
    browser_lib.wait_until_page_contains_element(button_locator)
    click_button(button_locator)


def click_button(button_locator):
    browser_lib.click_button(button_locator)


def search_for(term):
    input_field = "css:input[name='query']"
    browser_lib.input_text(input_field, term)
    browser_lib.press_keys(input_field, "ENTER")


def sort_by_latest():
    browser_lib.select_from_list_by_value(
        "css:select[data-testid='SearchForm-sortBy']", "newest")


def store_screenshot(filename):
    browser_lib.screenshot(filename=filename)


# Define a main() function that calls the other functions in order:
def main():
    try:
        open_the_website("https://www.nytimes.com/")

        click_agree_with_terms()

        click_search_button()
        search_for("russia")

        sort_by_latest()

        store_screenshot("output/screenshot.png")
    finally:
        browser_lib.close_all_browsers()


# Call the main() function, checking that we are running as a stand-alone script:
if __name__ == "__main__":
    main()
