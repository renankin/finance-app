#!/usr/bin/env python3

# Fetch statements from Nubank and Trading 212 accounts as a pandas DataFrame

from dotenv import load_dotenv
import pandas as pd
import os
import yfinance


load_dotenv()

PATH_TO_NUBANK = os.environ.get("PATH_TO_NUBANK")
PATH_TO_TRADING212 = os.environ.get("PATH_TO_TRADING212")


def fetch_nubank() -> pd.DataFrame:
    """
    Returns a dataframe with transactions from Nubank.
    """

    # List all files in a directory
    try:
        with os.scandir(PATH_TO_NUBANK) as entries:
            frames = []
            for entry in entries:
                if entry.is_file() and entry.name[-4:] == ".csv":
                    df = pd.read_csv(
                        filepath_or_buffer=f"{PATH_TO_NUBANK}/{entry.name}",
                        parse_dates=[1],
                        date_format="%d/%m/%Y",
                        na_values=["-", " -", " - "],
                    )

                    frames.append(df)

    except FileNotFoundError:
        print("There are no statement files from Nubank.")
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True)

    # Rename column names to English
    df.rename(
        columns={
            "Entrada/Saída": "Type",
            "Data": "Time",
            "Movimentação": "Action",
            "Produto": "Asset",
            "Instituição": "Institution",
            "Quantidade": "Quantity",
            "Preço unitário": "Asset Price",
            "Valor da Operação": "Total",
        },
        inplace=True
    )

    df.sort_values("Time", inplace=True)

    df["Currency (Total)"] = "BRL"

    # Tell when DataFrame was last updated
    last_date = df["Time"].iloc[-1]
    print(f"Last date in Nubank: {last_date.strftime("%d/%m/%Y")}")

    # Convert transactions to float
    df["Total"] = (
        df["Total"]
        .str.replace("R$", "")
        .str.replace(",", "")
    )
    df["Asset Price"] = (
        df["Asset Price"]
        .str.replace("R$", "")
        .str.replace(",", "")
    )
    df = df.astype({"Asset Price": float, "Total": float})

    # Clean up names from stocks
    df["Asset"] = df["Asset"].str.split(" - ").str[0]

    # Create new column with asset type
    def define_type(asset_name):
        if "Tesouro" in asset_name:
            return "Bond"
        if "Fundo" in asset_name:
            return "Managed Fund"
        else:
            return "Stock"
    df["Asset Type"] = df["Asset"].apply(define_type)

    # Replace stock names
    to_replace = {
        "ITSA1": "ITSA3",
        "ITSA2": "ITSA3",
        "ITSA4": "ITSA3",
        "TRPL3": "ISAE3",
    }
    df.replace(to_replace, inplace=True)

    # Adjust quantity based on stock splits
    df["Adjusted Quantity"] = df["Quantity"]

    ticker_list = df[df["Asset Type"] == "Stock"]["Asset"].unique()

    for ticker in ticker_list:

        if ticker != "CIEL3":

            # Load split data from yfinance
            data = yfinance.Ticker(f"{ticker}.SA").splits

            if not data.empty:

                # Reindex
                data = data.reindex(pd.to_datetime(
                    data.index)).tz_localize(None)

                ticker_df = df[df["Asset"] == ticker]
                splits = data[data.index > ticker_df["Time"].min()]

                # Iterate over rows of dataframe
                for index, row in ticker_df.iterrows():

                    # Calculate new adjusted quantity based on stock splits
                    qty = row["Quantity"]
                    for split_date, split_value in splits.items():
                        if row["Time"] < split_date:
                            qty *= split_value

                    df.loc[index, "Adjusted Quantity"] = round(qty)

    return df.reset_index()


def fetch_trading212():
    """
    Returns a dataframe with transactions from Trading 212.
    """

    frames = []

    try:
        with os.scandir(PATH_TO_TRADING212) as entries:
            for entry in entries:
                if entry.is_file() and entry.name[-4:] == ".csv":

                    df = pd.read_csv(
                        entry,
                        parse_dates=[1],
                        date_format="ISO8601",
                        header=0,
                    )

                    frames.append(df)

    except FileNotFoundError:
        print("There are no statement files from Trading 212.")
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True).sort_values("Time")

    # Tell when DataFrame was last updated
    last_date = df["Time"].iloc[-1]
    print(f"Last date in Trading 212: {last_date.strftime("%d/%m/%Y")}")

    return df


if __name__ == "__main__":
    fetch_nubank()
    fetch_trading212()
