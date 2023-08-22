import os
import urllib3
from RPA.Excel.Files import Files


def download_pictures(results):
    create_dir("output/images")
    for (index, result) in enumerate(results):
        picture_url = result[3]
        if picture_url:
            picture_filename = picture_url.split('/')[-1]
            # remove query string from url
            picture_filename = picture_filename.split('?')[0]
            extension = picture_filename.split('.')[-1]

            urllib3.request.urlretrieve(
                picture_url, f"output/images/{index}_{picture_filename}.{extension}")
            result[3] = picture_filename

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


def save_results(raw_results):
    raw_results = download_pictures(raw_results)
    results = raw_data_to_list_of_dictionary(raw_results)
    write_excel_worksheet("output/results.xlsx", "Fresh News", results)
    return results
