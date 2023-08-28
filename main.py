from RPA.Browser.Selenium import Selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
import re

from datetime import datetime
from app.locators import locators
from dateutil.relativedelta import relativedelta

from app.process_input import get_inputs
from app.save_results import save_results

browser_lib = Selenium()


def open_the_website(url: str):
    browser_lib.open_available_browser(
        url, options={"arguments": ["window-size=1920,1080"]})


def click_agree_with_terms():
    compliance_overlay_locator = locators.COMPLICANCE_OVERLAY_LOCATOR
    browser_lib.wait_until_page_contains_element(compliance_overlay_locator)
    compliance_overlay_button_locator = locators.COMPLICANCE_OVERLAY_BUTTON_LOCATOR
    click_button(compliance_overlay_button_locator)


def click_agree_with_cookie_policy():
    accept_cookies_button_locator = locators.ACCEPT_COOKIES_BUTTON_LOCATOR
    browser_lib.wait_until_page_contains_element(accept_cookies_button_locator)
    click_button(accept_cookies_button_locator)


def click_search_button():
    button_locator = locators.SEARCH_BUTTON_LOCATOR
    browser_lib.wait_until_page_contains_element(button_locator)
    click_button(button_locator)


def click_button(button_locator):
    browser_lib.click_button(button_locator)


def search_for(term: str):
    input_field = locators.INPUT_FIELD_LOCATOR
    browser_lib.input_text(input_field, term)
    browser_lib.press_keys(input_field, "ENTER")


def sort_by_latest():
    browser_lib.select_from_list_by_value(
        locators.SORT_DROPDOWN_LOCATOR, "newest")
    browser_lib.wait_until_element_does_not_contain(
        locators.SEARCH_FORM_STATUS_LOCATOR, "Loading")


def filter_by_sections(sections: list[str]):
    dropdown_locator = locators.SECTION_MULTISELECT_BUTTON_LOCATOR
    browser_lib.wait_and_click_button(dropdown_locator)

    options = browser_lib.find_elements(
        locators.SECTION_MULTISELECT_OPTIONS_LOCATOR)  # type: list[WebElement]
    options_text = [option.text for option in options]
    # Find Last character before the first Number
    # Example: 'U.S. Politics' -> 'U.S. Politics'
    # Example: 'U.S. Politics 1' -> 'U.S. Politics'
    options_text = [re.sub(r'\d.*', '', option) for option in options_text]
    options_text = [option.lower() for option in options_text]

    print("AVAILABLE SECTIONS:", options_text)

    for section in sections:
        print("TRYING TO CLICK SECTION:", section)
        try:
            option_index = options_text.index(section.lower())
            options[option_index].click()
            browser_lib.wait_until_element_does_not_contain(
                locators.SEARCH_FORM_STATUS_LOCATOR, "Loading")
        except ValueError:
            print("SECTION NOT FOUND:", section)


def filter_by_categories(categories: list[str]):
    dropdown_locator = locators.CATEGORY_MULTISELECT_BUTTON_LOCATOR
    browser_lib.wait_and_click_button(dropdown_locator)

    for category in categories:
        try:
            print("TRYING TO CLICK CATEGORY", category)
            checkbox_locator = f"css:div[data-testid='type'] ul[data-testid='multi-select-dropdown-list'] li input[value='{category}']"
            browser_lib.click_element_if_visible(checkbox_locator)
            browser_lib.wait_until_element_does_not_contain(
                locators.SEARCH_FORM_STATUS_LOCATOR, "Loading")
        except Exception as e:
            print("ERROR APPLYING CATEGORY FILTER:", category)
            print(e)


def parse_raw_date(date: str):
    # List of possible date formats
    # 'Jan. 7, 2022', 'Feb. 2, 2022', 'March 11, 2022, 'April 15, 2022' 'May 30, 2022', 'June 15, 2022', 'July 15, 2022', 'Aug. 15, 2022', 'Sept. 15, 2022', 'Oct. 15, 2022', 'Nov. 15, 2022', 'Dec. 15, 2022', 'Jan. 5', 'Feb. 5', 'March. 5', 'April 5', 'May 5', 'June 5', 'July 5', 'Aug. 5', 'Sept. 5', 'Oct. 5', 'Nov. 5', 'Dec. 5', '6h ago'
    # The format can be any of those, so we need to try them all
    # If the date is not in any of those formats, then we will just skip the date filter

    parsed_date = None

    # check if is '5h ago'
    if date.endswith('h ago'):
        hours = int(date.split('h')[0])
        parsed_date = datetime.now() - relativedelta(hours=hours)
    # extract month, day, and year
    else:
        year = datetime.now().year
        # detect if date has year
        if ',' in date:
            date = date.split(',')
            year = int(date[1].strip())
            date = date[0].strip()

        # extract day
        date = date.split(' ')
        day = int(date[1])
        date = date[0]

        # extract
        date = date.replace('.', '')
        months = ['Jan', 'Feb', 'March', 'April', 'May',
                  'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
        month = months.index(date) + 1

        parsed_date = datetime(year, month, day)

    return parsed_date


def results_length_change(browser: Selenium, current_length):
    elements = browser.find_elements(locators.SEARCH_RESULTS_LOCATOR)
    new_length = len(elements)
    return new_length > current_length


def apply_date_filter(min_date: datetime):
    elements = browser_lib.find_elements(
        locators.SEARCH_RESULTS_LOCATOR)  # type: list[WebElement]
    element = elements[-1]
    length = len(elements)

    date = element.find_element(By.CSS_SELECTOR,
                                locators.NEWS_DATE_TEXT_LOCATOR).text  # type: str
    date = parse_raw_date(date)

    search_more_locator = locators.SEARCH_SHOW_MORE_BUTTON_LOCATOR
    button_exists = len(browser_lib.find_elements(search_more_locator)) > 0

    while date > min_date and button_exists:
        while not browser_lib.is_element_visible(search_more_locator):
            browser_lib.scroll_element_into_view(search_more_locator)
        browser_lib.wait_and_click_button(search_more_locator)

        WebDriverWait(browser_lib, 60, poll_frequency=0.1).until(
            lambda browser: results_length_change(browser, length))

        elements = browser_lib.find_elements(locators.SEARCH_RESULTS_LOCATOR)
        element = elements[-1]
        length = len(elements)

        raw_date = element.find_element(By.CSS_SELECTOR,
                                        locators.NEWS_DATE_TEXT_LOCATOR).text  # type: str
        date = parse_raw_date(raw_date)
        button_exists = len(browser_lib.find_elements(search_more_locator)) > 0

        print("LAST RESULT DATE", date)


def check_if_contains_money(title: str, description: str):
    contains_money = False
    # Possible formats: $11.1 | $111,111.11 | 11 dollars | 11 USD
    # create regex to match all of those
    regexes = [
        r"\$\d+\.?\d*",  # $11.1 | $111.11
        r"\d+ dollars",  # 11 dollars
        r"\d+ USD"  # 11 USD
    ]
    for regex in regexes:
        if re.search(regex, title):
            contains_money = True
            break
        if description and re.search(regex, description):
            contains_money = True
            break
    return contains_money


def get_news_raw_results(search_phrase: str, min_date: datetime):
    elements = browser_lib.find_elements(
        locators.SEARCH_RESULTS_LOCATOR)  # type: list[WebElement]

    # Extract title, date, description, picture filename,
    # count of search phrases in the title and description,
    # True or False, depending on whether the title or description contains any amount of money
    results = []
    for element in elements:
        title = element.find_element(By.TAG_NAME,
                                     locators.NEWS_TITLE_LOCATOR).text
        raw_date = element.find_element(By.CSS_SELECTOR,
                                        locators.NEWS_DATE_TEXT_LOCATOR).text
        date = parse_raw_date(raw_date)

        # If the date is older than the min date, then we can stop
        if date < min_date:
            break

        date = date.strftime("%Y-%m-%d")

        try:
            description = element.find_element(By.CSS_SELECTOR,
                                               locators.NEWS_DESCRIPTION_LOCATOR).text
        except:
            description = None
        try:
            picture = element.find_element(By.CSS_SELECTOR,
                                           locators.NEWS_PICTURE_LOCATOR).get_attribute("src")
        except:
            picture = None

        search_phrase = search_phrase.lower()
        title_lowercase = title.lower()
        description_lowercase = description.lower() if description else None

        count_in_title = title_lowercase.count(search_phrase)
        count_in_description = 0
        if description:
            count_in_description = description_lowercase.count(
                search_phrase)

        contains_money = check_if_contains_money(title, description)

        results.append([title, date, description, picture,
                        count_in_title, count_in_description, contains_money])

    return results


# Define a main() function that calls the other functions in order:
def main():
    try:
        inputs = get_inputs()

        open_the_website("https://www.nytimes.com/")
        click_agree_with_terms()
        click_agree_with_cookie_policy()

        click_search_button()
        search_for(inputs["searchPhrase"])

        sort_by_latest()
        filter_by_sections(inputs["sections"])
        filter_by_categories(inputs["categories"])
        apply_date_filter(inputs["minDate"])
        raw_results = get_news_raw_results(
            inputs["searchPhrase"], inputs["minDate"])

        results = save_results(raw_results)
    finally:
        browser_lib.close_window()
        browser_lib.close_browser()
        browser_lib.close_all_browsers()


# Call the main() function, checking that we are running as a stand-alone script:
if __name__ == "__main__":
    main()
