from RPA.Robocorp.WorkItems import WorkItems
from datetime import datetime
from dateutil.relativedelta import relativedelta


default_inputs = {
    "searchPhrase": "Python",
    "numberOfMonths": 2,
    "categoryOrSections": "categories=article,interactivegraphics,video;sections=business,opinion,arts"
}


def get_inputs():
    inputs = {}
    try:
        inputs = validate_provided_inputs()
    except Exception as e:
        print(e)
        inputs = default_inputs
        print('Using default inputs')

    print("CATEGORIES AND SECTIONS: ", inputs["categoryOrSections"])

    categories_and_sections = extract_categories_and_sections(
        inputs["categoryOrSections"])

    inputs["categories"] = categories_and_sections["categories"]
    inputs["sections"] = categories_and_sections["sections"]

    min_date = calculate_mindate(inputs["numberOfMonths"])
    inputs["minDate"] = min_date

    print(inputs)
    return inputs


def validate_provided_inputs():
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

    return {
        "searchPhrase": payload["searchPhrase"],
        "numberOfMonths": payload["numberOfMonths"],
        "categoryOrSections": payload["categoryOrSections"]
    }


def calculate_mindate(number_of_months: int):
    today = datetime.today()

    # Subtract the number of months from today
    min_date = today

    # Set min date to the first day of the month
    min_date = min_date.replace(day=1)

    # Set min date time to 00:00:00
    min_date = min_date.replace(hour=0, minute=0, second=0, microsecond=0)

    if number_of_months > 0:
        # Subtract the number of months from today
        min_date = today - relativedelta(months=number_of_months)

    return min_date


def extract_categories_and_sections(categories_and_sections: str):
    categories_and_sections = categories_and_sections.split(";")

    categories = None
    sections = None
    if len(categories_and_sections) == 1:
        categories_and_sections = categories_and_sections[0]
        if categories_and_sections.startswith("categories="):
            categories = categories_and_sections.split("=")[1]
        elif categories_and_sections.startswith("sections="):
            sections = categories_and_sections.split("=")[1]

    if len(categories_and_sections) == 2:
        categories = categories_and_sections[0].split("=")[1]
        sections = categories_and_sections[1].split("=")[1]

    return {
        "categories": categories.split(",") if categories else None,
        "sections": sections.split(",") if sections else None
    }
