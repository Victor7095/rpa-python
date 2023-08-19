from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems
from RPA.Excel.Files import Files
from selenium.webdriver.common.by import By
import os

browser_lib = Selenium()


def get_inputs():
    wi = WorkItems()
    payload = wi.get_input_work_item().payload
    print(payload)
    return [payload["searchPhrase"], payload["numberOfMonths"], payload["categoryOrSections"]]


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


def get_news_raw_results():
    elements = browser_lib.find_elements(
        "css:ol[data-testid='search-results'] > li[data-testid='search-bodega-result']")

    # Extract title, date, description, picture filename, count of search phrases in the title and description, True or False, depending on whether the title or description contains any amount of money
    results = []
    for element in elements:
        print(element)
        title = element.find_element(By.TAG_NAME,
                                     "h4").text
        print(title)
        date = element.find_element(By.CSS_SELECTOR,
                                    "span[data-testid='todays-date']").text
        print(date)
        description = element.find_element(By.CSS_SELECTOR,
                                           "h4 + p").text
        print(description)
        picture = element.find_element(By.CSS_SELECTOR,
                                       "figure[aria-label='media'] img").get_attribute("src")
        print(picture)
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
        get_inputs()

        open_the_website("https://www.nytimes.com/")

        click_agree_with_terms()

        click_search_button()
        search_for("russia")

        sort_by_latest()

        raw_results = get_news_raw_results()

        results = raw_data_to_list_of_dictionary(raw_results)
        for result in results:
            print(result)

        write_excel_worksheet("output/results.xlsx", "Fresh News", results)
    finally:
        browser_lib.close_all_browsers()


# Call the main() function, checking that we are running as a stand-alone script:
if __name__ == "__main__":
    main()
