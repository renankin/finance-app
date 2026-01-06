#!/usr/bin/env python3

# Fetch prices for bonds from "Tesouro Transparente" website
# and stocks from yfinance

from datetime import datetime
import pandas as pd
import os
import requests
import yfinance as yf


# CSV path for bond prices
CSV_PATH = "prices.csv"


def save_bond_prices():
    """
    Scrape "Tesouro Transparente" portal and save daily prices from bonds
    in a csv file.
    """

    url = (
        "https://www.tesourotransparente.gov.br/ckan/dataset/"
        "df56aa42-484a-4a59-8184-7676580c81e3/resource/"
        "796d2059-14e9-44e3-80c9-2d9e30b405c1/download/"
        "precotaxatesourodireto.csv"
    )

    print(f"Trying to update {CSV_PATH} file.")
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        print("Failed to connect to server. Not updating bond prices.")
    else:
        with open(CSV_PATH, "w") as file:
            for line in response.iter_lines():
                file.write(line.decode("utf-8") + "\n")


def fetch_bond_price(bond_name) -> pd.DataFrame:
    """
    Returns a dataframe with the daily price for a bond scraped
    from "Tesouro Transparente" Portal
    """

    # Check if csv file exists
    if not os.path.exists(CSV_PATH):
        save_bond_prices()

    # Check if csv file has been updated today
    last_edited_time = os.path.getctime(CSV_PATH)
    time_dt = datetime.fromtimestamp(last_edited_time)
    if time_dt.date() != datetime.now().date():
        save_bond_prices()

    # Create dataframe with daily bond prices
    df = pd.read_csv(
        CSV_PATH,
        sep=";",
        decimal=",",
        parse_dates=[1, 2],
        date_format="%d/%m/%Y",
    )

    # Create new column with asset name
    df["Asset"] = (
        df["Tipo Titulo"]
        + " "
        + df["Data Vencimento"].dt.year.astype("string")
    )

    # Return prices for asset
    return df[df["Asset"] == bond_name].pivot_table(
        columns="Asset", index="Data Base", values="PU Venda Manha"
    )


def fetch_stock_price(ticker) -> pd.DataFrame:
    """
    Returns a dataframe with prices from stocks.
    The DataFrame is indexed on date from the first purchase until
    today's date. The columns are the stock names.
    """

    data = yf.Ticker(f"{ticker}.SA").history(period="max")

    return data["Close"]
