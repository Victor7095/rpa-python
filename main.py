from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems
from RPA.Excel.Files import Files
from selenium.webdriver.common.by import By
from datetime import datetime
import os
from dateutil.relativedelta import relativedelta

browser_lib = Selenium()


default_inputs = {
    "searchPhrase": "russia",
    "numberOfMonths": 12,
    "categoryOrSections": "world"
}


def get_inputs():
    inputs = {}
    try:
        wi = WorkItems()
        payload = wi.get_input_work_item().payload
        if "searchPhrase" not in payload:
            raise Exception("Missing searchPhrase")
        if "numberOfMonths" not in payload:
            raise Exception("Missing numberOfMonths")
        if "categoryOrSections" not in payload:
            raise Exception("Missing categoryOrSections")

        payload["numberOfMonths"] = int(payload["numberOfMonths"])
        if payload["numberOfMonths"] < 0:
            raise Exception("numberOfMonths cannot be negative")

        inputs = {
            "searchPhrase": payload["searchPhrase"],
            "numberOfMonths": payload["numberOfMonths"],
            "categoryOrSections": payload["categoryOrSections"]
        }
    except Exception as e:
        print(e)
        inputs = default_inputs
        print('Using default inputs')
        print(inputs)

    max_date = calculate_maxdate(inputs["numberOfMonths"])
    inputs["maxDate"] = max_date
    return inputs


def calculate_maxdate(number_of_months):
    today = datetime.today()

    # Subtract the number of months from today
    max_date = today

    # Set max date to the first day of the month
    max_date = max_date.replace(day=1)

    # Set max date time to 00:00:00
    max_date = max_date.replace(hour=0, minute=0, second=0, microsecond=0)

    if number_of_months > 0:
        # Subtract the number of months from today
        max_date = today - relativedelta(months=number_of_months)

    return max_date


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
    # WebDriverWait(browser_lib, 10).until(EC)
    browser_lib.wait_until_element_does_not_contain(
        "css:p[data-testid='SearchForm-status']", "Loading")


def parse_raw_date(date):
    print(date)
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


def apply_date_filter(max_date):
    elements = browser_lib.find_elements(
        "css:ol[data-testid='search-results'] > li[data-testid='search-bodega-result']")
    element = elements[-1]
    date = element.find_element(By.CSS_SELECTOR,
                                "span[data-testid='todays-date']").text  # type: str

    print(parse_raw_date(date))


def get_news_raw_results():
    elements = browser_lib.find_elements(
        "css:ol[data-testid='search-results'] > li[data-testid='search-bodega-result']")

    # Extract title, date, description, picture filename, count of search phrases in the title and description, True or False, depending on whether the title or description contains any amount of money
    results = []
    for element in elements:
        title = element.find_element(By.TAG_NAME,
                                     "h4").text
        date = element.find_element(By.CSS_SELECTOR,
                                    "span[data-testid='todays-date']").text
        description = element.find_element(By.CSS_SELECTOR,
                                           "h4 + p").text
        picture = element.find_element(By.CSS_SELECTOR,
                                       "figure[aria-label='media'] img").get_attribute("src")
        count_of_search_phrases_in_title = 0
        count_of_search_phrases_in_description = 0
        contains_money = False
        results.append([title, date, description, picture,
                        count_of_search_phrases_in_title, count_of_search_phrases_in_description, contains_money])

    return results


def raw_data_to_list_of_dictionary(raw_data):
    # Convert raw data to a list of dictionaries
    results = []
    for row in raw_data:
        results.append({
            "title": row[0],
            "date": row[1],
            "description": row[2],
            "picture": row[3],
            "count_of_search_phrases_in_title": row[4],
            "count_of_search_phrases_in_description": row[5],
            "contains_money": row[6]
        })

    return results


def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def write_excel_worksheet(path, worksheet, data):
    create_dir("output")
    lib = Files()
    lib.create_workbook(path)
    try:
        lib.create_worksheet(worksheet, content=data, header=True)
        lib.save_workbook()
    finally:
        lib.close_workbook()


# Define a main() function that calls the other functions in order:
def main():
    try:
        inputs = get_inputs()

        open_the_website("https://www.nytimes.com/")

        click_agree_with_terms()

        click_search_button()
        search_for(inputs["searchPhrase"])

        sort_by_latest()
        apply_date_filter(inputs["maxDate"])

        raw_results = get_news_raw_results()

        results = raw_data_to_list_of_dictionary(raw_results)

        write_excel_worksheet("output/results.xlsx", "Fresh News", results)
    finally:
        browser_lib.close_window()
        browser_lib.close_browser()
        browser_lib.close_all_browsers()


# Call the main() function, checking that we are running as a stand-alone script:
if __name__ == "__main__":
    main()
