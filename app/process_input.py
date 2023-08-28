import os
from venv import logger
from RPA.Robocorp.WorkItems import WorkItems
from datetime import datetime
from dateutil.relativedelta import relativedelta
import structlog


class ProcessInput:
    logger: structlog.PrintLogger = structlog.get_logger()

    @staticmethod
    def default_inputs():
        return {
            "searchPhrase": "Python",
            "numberOfMonths": 2,
            "categories": ["article", "interactivegraphics", "video"],
            "sections": ["business", "opinion", "arts"]
        }

    def get_inputs(self):
        self.logger.info("Getting inputs")
        # load inputs from .env file
        try:
            inputs = {
                "searchPhrase": os.environ.get("searchPhrase"),
                "numberOfMonths": int(os.environ.get("numberOfMonths")),
                "categories": os.environ.get("categories").split(","),
                "sections": os.environ.get("sections").split(",")
            }
        except Exception as e:
            self.logger.error(
                "Using default inputs because of error: " + str(e))
            inputs = self.default_inputs()

        #  Try loading inputs from work item
        try:
            inputs = self.load_inputs_from_work_item()
        except Exception as e:
            self.logger.error(
                "Using .env variables because of error: " + str(e))

        # Calculate minumim date
        min_date = self.calculate_mindate(inputs["numberOfMonths"])
        inputs["minDate"] = min_date

        self.logger.info(f"Inputs: {inputs}")
        return inputs

    # Validate inputs provided by work item
    def load_inputs_from_work_item(self):
        self.logger.info("Checking work item for inputs")
        wi = WorkItems()
        payload = wi.get_input_work_item().payload
        if "searchPhrase" not in payload:
            raise Exception("Missing searchPhrase")
        if "numberOfMonths" not in payload:
            raise Exception("Missing numberOfMonths")
        if "categories" not in payload:
            raise Exception("Missing categories")
        if "sections" not in payload:
            raise Exception("Missing sections")

        payload["numberOfMonths"] = int(payload["numberOfMonths"])
        if payload["numberOfMonths"] < 0:
            raise Exception("numberOfMonths cannot be negative")

        return {
            "searchPhrase": payload["searchPhrase"],
            "numberOfMonths": payload["numberOfMonths"],
            "categories": payload["categories"],
            "sections": payload["sections"]
        }

    # Min Date is oldest date to search for
    def calculate_mindate(self, number_of_months: int):
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
