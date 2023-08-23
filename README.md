# RPA Challenge - Fresh news

This bot is a Python script that searches for news articles containing a specific phrase and checks if they mention money. Here's how to install the dependencies and run the bot:

## Run in Robocorp Cloud

The parameters must follow the format:

```json
{
    "searchPhrase": "russia", //any word or phrase
    "numberOfMonths": 1,      //number of months to search
    "categoryOrSections": "categories=article,interactivegraphics,video;sections=business,opinion,arts"
}

```

## Installation

1. Install Python 3.x from the official website: https://www.python.org/downloads/
2. Clone this repository to your local machine using Git or download the ZIP file and extract it.
3. Open a terminal or command prompt and navigate to the directory where you cloned or extracted the repository.
4. Run the following command to install the required Python packages:

```
pip install -r requirements.txt
```

## Usage

1. Open the `process_input.py` file in a text editor or IDE.
2. Set the `default_inputs` values to the phrase and news category or sections you want to search for.
3. Save the file.
4. Open a terminal or command prompt and navigate to the directory where you cloned or extracted the repository.
5. Run the following command to start the bot:

```
python main.py
```

The bot will search for news articles containing the specified phrase and save them to a excel file. You can customize the bot's behavior by modifying the code in `main.py`.
