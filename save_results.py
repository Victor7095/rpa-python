import os
from urllib.request import urlretrieve
from RPA.Excel.Files import Files
from pathlib import Path
import shutil


def download_pictures(results: list):
    for (index, result) in enumerate(results):
        picture_url = result[3]
        if picture_url:
            picture_filename = picture_url.split('/')[-1]
            # remove query string from url
            picture_filename = picture_filename.split('?')[0]
            extension = picture_filename.split('.')[-1]

            urlretrieve(
                picture_url, f"output/{index}_{picture_filename}.{extension}")
            result[3] = picture_filename

    return results


def raw_data_to_list_of_dictionary(raw_data: list):
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


def create_dir(directory: str):
    dirpath = Path('output')
    if dirpath.exists() and dirpath.is_dir():
        shutil.rmtree(dirpath)
    os.makedirs(directory)


def write_excel_worksheet(path: str, worksheet: str, data: list):
    lib = Files()
    lib.create_workbook(path, sheet_name=worksheet)
    try:
        lib.append_rows_to_worksheet(content=data, header=True)
        lib.save_workbook()
    finally:
        lib.close_workbook()


def save_results(raw_results):
    create_dir("output")
    raw_results = download_pictures(raw_results)
    results = raw_data_to_list_of_dictionary(raw_results)
    write_excel_worksheet("output/results.xlsx", "Fresh News", results)
    return results
