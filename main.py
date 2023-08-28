from dotenv import load_dotenv
import structlog
from app.bot_pipeline import BotPipeline
from app.process_input import ProcessInput
from app.save_results import save_results


load_dotenv("../")


# Define a main() function that calls the other functions in order:
def main():
    inputs = ProcessInput().get_inputs()
    bot_pipeline = BotPipeline(inputs)
    raw_results = bot_pipeline.run()
    return
    save_results(raw_results)


# Call the main() function, checking that we are running as a stand-alone script:
if __name__ == "__main__":
    main()
