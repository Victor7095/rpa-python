from RPA.Browser.Selenium import Selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from dateutil.relativedelta import relativedelta
from datetime import datetime
import structlog
import re

from app import locators


class BotPipeline:
    browser_lib = Selenium()
    inputs: dict[str, any]
    logger: structlog.PrintLogger = structlog.get_logger()

    def __init__(self, inputs: dict):
        self.inputs = inputs

    def open_the_website(self, url: str):
        self.browser_lib.open_available_browser(
            url, options={"arguments": ["window-size=1920,1080"]})

    def click_agree_with_terms(self):
        compliance_overlay_locator = locators.COMPLICANCE_OVERLAY_LOCATOR
        self.browser_lib.wait_until_page_contains_element(
            compliance_overlay_locator)
        compliance_overlay_button_locator = locators.COMPLICANCE_OVERLAY_BUTTON_LOCATOR
        self.browser_lib.click_button(compliance_overlay_button_locator)

    def click_agree_with_cookie_policy(self, ):
        accept_cookies_button_locator = locators.ACCEPT_COOKIES_BUTTON_LOCATOR
        self.browser_lib.wait_until_page_contains_element(
            accept_cookies_button_locator)
        self.browser_lib.click_button(accept_cookies_button_locator)

    def click_search_button(self, ):
        button_locator = locators.SEARCH_BUTTON_LOCATOR
        self.browser_lib.wait_until_page_contains_element(button_locator)
        self.browser_lib.click_button(button_locator)

    def search_for(self, term: str):
        input_field = locators.INPUT_FIELD_LOCATOR
        self.browser_lib.input_text(input_field, term)
        self.browser_lib.press_keys(input_field, "ENTER")

    def sort_by_latest(self):
        self.browser_lib.select_from_list_by_value(
            locators.SORT_DROPDOWN_LOCATOR, "newest")
        self.browser_lib.wait_until_element_does_not_contain(
            locators.SEARCH_FORM_STATUS_LOCATOR, "Loading")

    def filter_by_sections(self, sections: list[str]):
        dropdown_locator = locators.SECTION_MULTISELECT_BUTTON_LOCATOR
        self.browser_lib.wait_and_click_button(dropdown_locator)

        options = self.browser_lib.find_elements(
            locators.SECTION_MULTISELECT_OPTIONS_LOCATOR)  # type: list[WebElement]
        options_text = [option.text for option in options]
        # Find Last character before the first Number
        # Example: 'U.S. Politics' -> 'U.S. Politics'
        # Example: 'U.S. Politics 1' -> 'U.S. Politics'
        options_text = [re.sub(r'\d.*', '', option) for option in options_text]
        options_text = [option.lower() for option in options_text]

        self.logger.info(f"AVAILABLE SECTIONS: {options_text}")

        for section in sections:
            self.logger.info(f"APPLYING SECTION FILTER: {section}")
            try:
                option_index = options_text.index(section.lower())
                options[option_index].click()
                self.browser_lib.wait_until_element_does_not_contain(
                    locators.SEARCH_FORM_STATUS_LOCATOR, "Loading")
            except ValueError:
                self.logger.info(f"SECTION NOT FOUND: {section}")

    def filter_by_categories(self, categories: list[str]):
        dropdown_locator = locators.CATEGORY_MULTISELECT_BUTTON_LOCATOR
        self.browser_lib.wait_and_click_button(dropdown_locator)

        for category in categories:
            try:
                self.logger.info(f"APPLYING CATEGORY FILTER: {category}")
                checkbox_locator = f"css:div[data-testid='type'] ul[data-testid='multi-select-dropdown-list'] li input[value='{category}']"
                self.browser_lib.click_element_if_visible(checkbox_locator)
                self.browser_lib.wait_until_element_does_not_contain(
                    locators.SEARCH_FORM_STATUS_LOCATOR, "Loading")
            except Exception as e:
                self.logger.error(
                    f"ERROR APPLYING CATEGORY FILTER: {category}")
                self.logger.exception(e)

    def parse_raw_date(self, date: str):
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

    def results_length_change(self, browser: Selenium, current_length):
        elements = browser.find_elements(locators.SEARCH_RESULTS_LOCATOR)
        new_length = len(elements)
        return new_length > current_length

    def apply_date_filter(self, min_date: datetime):
        elements = self.browser_lib.find_elements(
            locators.SEARCH_RESULTS_LOCATOR)  # type: list[WebElement]
        element = elements[-1]
        length = len(elements)

        date = element.find_element(By.CSS_SELECTOR,
                                    locators.NEWS_DATE_TEXT_LOCATOR).text  # type: str
        date = self.parse_raw_date(date)

        search_more_locator = locators.SEARCH_SHOW_MORE_BUTTON_LOCATOR
        button_exists = len(
            self.browser_lib.find_elements(search_more_locator)) > 0

        while date > min_date and button_exists:
            self.logger.info("LOADING MORE RESULTS")
            while not self.browser_lib.is_element_visible(search_more_locator):
                self.browser_lib.scroll_element_into_view(search_more_locator)
            self.browser_lib.wait_and_click_button(search_more_locator)

            WebDriverWait(self.browser_lib, 60, poll_frequency=0.1).until(
                lambda browser: self.results_length_change(browser, length))

            elements = self.browser_lib.find_elements(
                locators.SEARCH_RESULTS_LOCATOR)
            element = elements[-1]
            length = len(elements)

            raw_date = element.find_element(By.CSS_SELECTOR,
                                            locators.NEWS_DATE_TEXT_LOCATOR).text  # type: str
            date = self.parse_raw_date(raw_date)
            button_exists = len(
                self.browser_lib.find_elements(search_more_locator)) > 0

            self.logger.info(f"LAST RESULT DATE: {date}")

    def check_if_contains_money(self, title: str, description: str):
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

    def get_news_raw_results(self, search_phrase: str, min_date: datetime):
        elements = self.browser_lib.find_elements(
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
            date = self.parse_raw_date(raw_date)

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

            contains_money = self.check_if_contains_money(title, description)

            results.append([title, date, description, picture,
                            count_in_title, count_in_description, contains_money])

        return results

    def run(self):
        try:
            self.open_the_website("https://www.nytimes.com/")
            self.click_agree_with_terms()
            self.click_agree_with_cookie_policy()

            self.click_search_button()
            self.search_for(self.inputs["searchPhrase"])

            self.sort_by_latest()
            self.filter_by_sections(self.inputs["sections"])
            self.filter_by_categories(self.inputs["categories"])
            self.apply_date_filter(self.inputs["minDate"])
            raw_results = self.get_news_raw_results(
                self.inputs["searchPhrase"], self.inputs["minDate"])

            return raw_results
        finally:
            self.browser_lib.close_window()
            self.browser_lib.close_browser()
            self.browser_lib.close_all_browsers()
