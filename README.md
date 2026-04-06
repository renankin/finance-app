## About

`finance_app` is a web app written in Python with Flask and it is meant to keep track of stocks across different accounts.

It uses `yfinance` in the background for fetching the current price and stock splits to give an overview of current balance. The SQLite database runs locally inside the `instance/` folder which is created upon initialisation.

## How to run it

First you need to create a Python virtual environment (I recommend using `pyenv`).

Then install the requirements:

```bash
pip install -r "requirements.txt"
```

After that you should be able to run it with:
```bash
flask --app finance_app run
```

## Current functionatilies

* Searches for a stock from `yfinance` server to show the stocks splits and current price.
* Allows to add a transaction into the database.
* Display a history of transactions and enable to edit or delete.
* Show history of dividends.
* Display Return on Investment (ROI) for each asset by calculating internal rate of return (RRI) and absolute return. This takes into consideration the dividends paid for the given stock.
