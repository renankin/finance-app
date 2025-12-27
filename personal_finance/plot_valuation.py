#!/usr/bin/env python3

# Plots the daily valuation from Nubank and Trading 212 accounts

from datetime import datetime
from dotenv import load_dotenv
from fetch_holdings import fetch_nubank, fetch_trading212
import numpy as np
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import os
import requests
import yfinance as yf


load_dotenv()

# Path for saving "Tesouro direto" prices
CSV_PATH = Path(__file__).resolve().parent.parent / "prices.csv"


def main():

    # Load Nubank data and compute valuation
    nubank_df = fetch_nubank()
    nu_val = nubank_valuation(nubank_df)

    # Load Trading 212 data and compute valuation
    trading212_df = fetch_trading212()
    trading212_val = trading212_valuation(trading212_df)
    trading212_val = trading212_val.reindex(nu_val.index).ffill()

    # Asks for input on which exchange rate to use
    currency = ""
    while currency not in ["GBP", "BRL"]:
        currency = input("Choose currency to plot (GBP/BRL): ").upper()

    if currency != nubank_df["Currency (Total)"].unique():
        nu_val = exchange_currency(nu_val, currency)

    if currency != trading212_df["Currency (Total)"].unique():
        trading212_val = exchange_currency(trading212_val, currency)

    # Combine Nubank and Trading 212
    merged_df = nu_val.join(trading212_val)
    merged_df["Total"] = merged_df.sum(axis=1)

    plot_price_history(merged_df, currency)


def exchange_currency(df, currency):
    """
    Multiplies dataframe by exchange rate (either GBP or BRL).
    """

    # Find exchange rate GBP to BRL
    print("Converting GBP to BRL...")
    ticker = "GBPBRL=X"
    data = yf.download(
        ticker,
        start=df.index.min().date(),
        end=datetime.now().date(),
        interval="1d",
        auto_adjust=True,
    )
    data = data.reindex(df.index).ffill()

    if currency == "GBP":
        exchange_rate = 1 / data["Close"][ticker]
    else:
        exchange_rate = data["Close"][ticker]

    return df.mul(exchange_rate, axis=0)


def save_prices_csv():
    """
    Scrape "Tesouro Transparente" portal and save daily prices from bonds
    in a csv file.
    """

    print(f"Updating {CSV_PATH} file . . .")

    url = (
        "https://www.tesourotransparente.gov.br/ckan/dataset/"
        "df56aa42-484a-4a59-8184-7676580c81e3/resource/"
        "796d2059-14e9-44e3-80c9-2d9e30b405c1/download/"
        "precotaxatesourodireto.csv"
    )

    response = requests.get(url)

    with open(CSV_PATH, "w") as file:
        for line in response.iter_lines():
            file.write(line.decode("utf-8") + "\n")


def fetch_bond_prices(nubank_df) -> pd.DataFrame:
    """
    Returns a dataframe with the daily prices from bonds scraped
    from "Tesouro Transparente" Portal
    """

    print("Fetching bond prices to compute Nubank valuation...")

    # Check if csv file exists
    if not os.path.exists(CSV_PATH):
        save_prices_csv()

    # Check if csv file has been updated today
    last_edited_time = os.path.getctime(CSV_PATH)
    time_dt = datetime.fromtimestamp(last_edited_time)
    if time_dt.date() != datetime.now().date():
        save_prices_csv()

    # Create dataframe with daily bond prices
    try:
        price_data = pd.read_csv(
            CSV_PATH,
            sep=";",
            decimal=",",
            parse_dates=[1, 2],
            date_format="%d/%m/%Y",
        )
    except FileNotFoundError:
        return pd.DataFrame()

    # Create new column with asset name
    price_data["Asset"] = (
        price_data["Tipo Titulo"]
        + " "
        + price_data["Data Vencimento"].dt.year.astype("string")
    )

    # Filter dataframe with bonds and date contained in holdings
    bond_names = nubank_df[
        nubank_df.loc[:, "Asset Type"] == "Bond"
    ]["Asset"].unique()

    df_filtered = price_data.loc[
        (price_data["Asset"].isin(bond_names))
        & (price_data["Data Base"] > nubank_df["Time"].min())
    ]

    # Pivot dataframe to create new columns for each bond
    prices_df = df_filtered.pivot_table(
        columns="Asset", index="Data Base", values="PU Venda Manha"
    )

    return prices_df


def fetch_stock_prices(nubank_df) -> pd.DataFrame:
    """
    Returns a dataframe with prices from stocks.
    The DataFrame is indexed on date from the first purchase until
    today's date. The columns are the stock names.
    """

    stocks = nubank_df[nubank_df["Asset Type"] == "Stock"]["Asset"].unique()

    tickers = [f"{stock}.SA" for stock in stocks if stock != "CIEL3"]

    print("Fetching stock prices to compute Nubank valuation...")
    data = yf.download(
        tickers,
        start=nubank_df["Time"].min().date(),
        end=datetime.now().date(),
        interval="1d",
        auto_adjust=True,
    )

    # Rename columns so that is the same name as nubank DataFrame
    columns_dict = {ticker: ticker.replace(".SA", "") for ticker in tickers}

    return data["Close"].rename(columns=columns_dict)


def nubank_valuation(nubank_df) -> pd.DataFrame:
    """
    Returns a dataframe indexed with the daily price history
    for each asset of Nubank.
    """

    # Filter relevant transactions
    df = nubank_df[
        nubank_df["Action"]
        .isin(["Compra", "Transferência - Liquidação", "Resgate", "Venda"])
    ].copy()

    # Make sale quantities negative (bonds)
    df.loc[
        df["Action"].isin(["Resgate", "Venda"]),
        "Adjusted Quantity"
    ] = -1 * df["Adjusted Quantity"]

    # Make sale quantities negative (stock)
    df.loc[
        (df["Action"] == "Transferência - Liquidação")
        & (df["Type"] == "Debito"),
        "Adjusted Quantity",
    ] = -1 * df["Adjusted Quantity"]

    # Compute cumulative sum from adjusted quantitities
    df["Cumsum"] = (
        df.groupby("Asset")["Adjusted Quantity"].cumsum()
    )

    # Pivot dataframe to create a new one with cum sum
    cumsum_df = df.pivot_table(
        index="Time", columns="Asset", values="Cumsum"
    )

    # Create a daily index from holdings
    portfolio_dates = pd.date_range(
        start=nubank_df["Time"].min(), end=datetime.now(), freq="D"
    )

    # Expand cumsum_df and prices to daily frequency and compute valuation
    cumsum_df = cumsum_df.reindex(portfolio_dates).ffill()
    prices_df = (
        fetch_bond_prices(nubank_df)
        .join(fetch_stock_prices(nubank_df))
    )
    prices_df = prices_df.reindex(portfolio_dates).ffill()
    valuation_df = cumsum_df * prices_df

    # Delete assets which do not have prices
    diff = set(cumsum_df.columns) - set(prices_df.columns)
    valuation_df.drop(diff, axis=1, inplace=True)

    # Include them in valuation
    for asset in diff:

        # Calculate valuation for asset
        asset_df = df[df["Asset"] == asset].copy()
        asset_df["Valuation"] = (
            asset_df["Cumsum"] * asset_df["Asset Price"]
        )

        # Reshape dataframe to include them in valuation
        pivot_df = asset_df.pivot_table(
            index="Time", columns="Asset", values="Valuation"
        )
        pivot_df = pivot_df.reindex(portfolio_dates).ffill()

        # Include in valuation DataFrame
        valuation_df.join(pivot_df)

    # Replace NaN values with 0's
    valuation_df.fillna(0, inplace=True)

    return valuation_df


def trading212_valuation(trading212_df) -> pd.DataFrame:
    """
    Returns a dataframe indexed with the daily price history from Trading 212.
    """

    # Obtain cummulative sum of values over time
    trading212_df["Trading 212"] = trading212_df["Total"].cumsum()

    # Get only date to conform to Nubank
    trading212_df["Time"] = trading212_df["Time"].dt.date

    # Reshape DataFrame to get valuation
    cumsum_df = trading212_df.pivot_table(index="Time", values="Trading 212")

    return cumsum_df


def plot_price_history(df, currency):
    """
    Plots the price history using plotly with dropdown menu for each asset.
    Exchange the currency which needs to be input as a three-digit code.
    """

    asset_names = df.columns
    trace_visibility = []

    for num in range(len(asset_names)):
        vis = np.zeros(len(asset_names), dtype=bool)
        vis[num] = True
        trace_visibility.append(vis)

    fig = go.Figure()
    graph_buttons = []

    for index, bond_name in enumerate(asset_names):

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[bond_name],
                # name=f"IRR:{irr:.2%}",
                visible=True if bond_name == "Total" else False,
                showlegend=True,
            )
        )

        graph_buttons.append(
            {
                "label": bond_name,
                "method": "update",
                "args": [{"visible": trace_visibility[index],
                          "title": bond_name}],
            }
        )

    fig.update_layout(
        updatemenus=[
            {"active": asset_names.get_loc("Total"), "buttons": graph_buttons}
        ],
        title_text="Capital Evolution",
        xaxis_title="Date",
        yaxis_title=f"Value ({currency})",
    )

    fig.show(renderer="browser")


if __name__ == "__main__":

    main()
