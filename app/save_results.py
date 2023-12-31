import os
from urllib.request import urlretrieve
from RPA.Excel.Files import Files
from pathlib import Path
import shutil

import structlog


class Output:
    logger: structlog.PrintLogger = structlog.get_logger()

    @staticmethod
    def download_pictures(results: list):
        Output.logger.info("Downloading pictures")
        for (index, result) in enumerate(results):
            picture_url = result[3]
            if picture_url:
                try:
                    picture_filename = picture_url.split('/')[-1]
                    # remove query string from url
                    picture_filename = picture_filename.split('?')[0]
                    picture_filename = f"{index + 1}_{picture_filename}"
                    urlretrieve(
                        picture_url, f"output/{picture_filename}")
                    result[3] = picture_filename
                except:
                    result[3] = None

        return results

    @staticmethod
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

    @staticmethod
    def create_dir(directory: str):
        dirpath = Path('output')
        if dirpath.exists() and dirpath.is_dir():
            shutil.rmtree(dirpath)
        os.makedirs(directory)

    @staticmethod
    def write_excel_worksheet(path: str, worksheet: str, data: list):
        Output.logger.info("Writing results to excel")
        lib = Files()
        lib.create_workbook(path, sheet_name=worksheet)
        try:
            lib.append_rows_to_worksheet(content=data, header=True)
            lib.save_workbook()
        finally:
            lib.close_workbook()

    @staticmethod
    def save_results(raw_results):
        Output.create_dir("output")
        raw_results = Output.download_pictures(raw_results)
        results = Output.raw_data_to_list_of_dictionary(raw_results)
        Output.write_excel_worksheet(
            "output/results.xlsx", "Fresh News", results)
        Output.logger.info("Results saved to output/results.xlsx")
        return results
