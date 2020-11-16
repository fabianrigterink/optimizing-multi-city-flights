# Optimizing multi-city flights using the Skyscanner API and NEOS

## Introduction

This repository allows you to provide
- a list of cities/airports including a home city,
- a date range to travel these cities,
- minimum and maximum number of days to stay in these cities.

From the "src/main.py" script, using both the "Quotes" and "Solver" clients, the user can then find the cheapest trip that traverses all the cities -- departing from and returning to the home city. Two instances (the 2019 top 10 and top 20 travel destinations, see __[here](https://www.cnn.com/travel/article/most-visited-cities-euromonitor-2019/index.html)__ and __[here](https://go.euromonitor.com/white-paper-travel-2019-100-cities)__) are given as examples. Behind the scenes, the Quotes client uses the Skyscanner API to retrieve cached quotes for flights. To find the cost-minimizing trip, the Solver client uses NEOS to solve the corresponding optimization problem.

## Before running "src/main.py"

Before running "src/main.py", make sure you have done the following:
1. Created a virtual environment (e.g., "venv"). You can do so by running `virtualenv venv`.
2. Activated the virtual environment. You can do so by running
    - `venv/Scripts/activate` on Windows or
    - `. venv/bin/activate` on Linux.
3. Installed all packages using `pip install -r requirements.txt`.
4. Created a "config.ini" file at the parent directory level. This file has the following content:
    ```
    [DEFAULT]
    RAPIDAPI_SKYSCANNER_KEY = <your Skyscanner API key>
    RAPIDAPI_SKYSCANNER_HOST = <the Skyscanner API host>
    ```
    You can generate a Skyscanner API key for free at __[RapidAPI](https://rapidapi.com/)__. You will also find the host there.

## Running "src/main.py"

After activating the virtual environment, run "src/main.py" from the parent directory level: `python src/main.py`.

You can run your own instance by creating a "src/instance_...py" file and importing it in "src/main.py".

Once an instance is imported, you can use the flags to run only certain parts of the code. It is good practice to
1. First, run with `flag_get_city_ids = True` (all other flags set to `False`), given only `place_names`.
2. Then, run with `flag_get_quotes = True` (all other flags set to `False`), given the `city_ids` from Step 1.
3. Last, run with `flag_solve = True` (all other flags set to `False`), given the "data/quotes_...csv" file from Step 2.

*Happy traveling!*