#!/usr/bin/env python3

# Create a SQLite database with transactions and prices
# from Nubank and Trading 212 assets

import datetime as dt
from dotenv import load_dotenv
import pandas as pd
import os
import requests
import sqlite3
import yfinance as yf
from zoneinfo import ZoneInfo

load_dotenv()

DB_NAME = "transactions.db"
NUBANK_PATH = os.environ.get("PATH_TO_NUBANK")
TRADING212_PATH = os.environ.get("PATH_TO_TRADING212")


def main():
    """
    Initialises a database with transactions from Nubank and Trading 212.
    """

    with sqlite3.connect(DB_NAME) as db:

        if wants_to_create(DB_NAME):
            create_db(db)
        else:
            include_accounts(db)
            include_assets(db)
            include_transactions(db)
            include_bond_prices(db)
            include_stock_prices(db)
            include_currencies(db)


def create_db(conn):
    """
    Create tables for database.
    """

    if wants_to_create("accounts"):
        conn.execute("DROP TABLE IF EXISTS accounts")
        conn.execute(
            """
            CREATE TABLE accounts (
                account_id INTEGER PRIMARY KEY,
                account_name VARCHAR(50) NOT NULL UNIQUE,
                currency CHAR(3) NOT NULL
            )
            """
        )
        include_accounts(conn)

    if wants_to_create("assets"):
        conn.execute("DROP TABLE IF EXISTS assets")
        conn.execute(
            """
            CREATE TABLE assets (
                asset_id INTEGER PRIMARY KEY,
                asset_name VARCHAR(50) NOT NULL UNIQUE,
                purchase_date DATETIME,
                asset_type VARCHAR(25) NOT NULL,
                account_id INT NOT NULL,
                position_open INT NOT NULL,
                FOREIGN KEY (account_id) REFERENCES accounts(account_id)
            )
            """
        )
        include_assets(conn)

    if wants_to_create("transactions"):
        conn.execute("DROP TABLE IF EXISTS transactions")
        conn.execute(
            """
            CREATE TABLE transactions (
                date DATE NOT NULL,
                asset_id INT NOT NULL,
                transaction_type VARCHAR(50) NOT NULL,
                total_value REAL NOT NULL,
                FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
                UNIQUE (date, asset_id, transaction_type, total_value)
            )
            """
        )
        include_transactions(conn)

    if wants_to_create("prices"):
        conn.execute("DROP TABLE IF EXISTS prices")
        conn.execute(
            """
            CREATE TABLE prices (
                date DATETIME NOT NULL,
                asset_id INT NOT NULL,
                unit_price FLOAT NOT NULL,
                FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
                UNIQUE (date, asset_id)
            )
            """
        )
        include_bond_prices(conn)
        include_stock_prices(conn)

    if wants_to_create("currencies"):
        conn.execute("DROP TABLE IF EXISTS currencies")
        conn.execute(
            """
            CREATE TABLE currencies (
                date DATE PRIMARY KEY,
                exchange_rate FLOAT NOT NULL
            )
            """
        )
        include_currencies(conn)


def fetch_transactions() -> pd.DataFrame:
    """

    """

    # Load Nubank transactions into dataframe
    try:
        with os.scandir(NUBANK_PATH) as entries:
            frames = []
            for entry in entries:
                if entry.is_file() and entry.name[-4:] == ".csv":
                    df = pd.read_csv(
                        f"{NUBANK_PATH}/{entry.name}",
                        header=0,
                        names=[
                            "cashflow", "date", "transaction_type",
                            "asset_name", "account_name", "quantity",
                            "unit_price", "total_value"
                        ],
                        parse_dates=[1],
                        date_format="%d/%m/%Y",
                        na_values=["-", " -", " - "],
                    )

                    frames.append(df)

    except FileNotFoundError:
        print("There are no statement files from Nubank.")
        return

    df_nubank = pd.concat(frames)

    df_nubank["currency"] = "BRL"

    # Convert transactions to float
    df_nubank["total_value"] = (
        df_nubank["total_value"]
        .str.replace("R$", "")
        .str.replace(",", "")
    )
    df_nubank["unit_price"] = (
        df_nubank["unit_price"]
        .str.replace("R$", "")
        .str.replace(",", "")
    )
    df_nubank = df_nubank.astype({
        "unit_price": float, "total_value": float}
    )

    # Clean up names from stocks
    df_nubank["asset_name"] = (
        df_nubank["asset_name"]
        .str.split(" - ").str[0]
    )

    # Replace stock names
    asset_map = {
        "ITSA1": "ITSA3",
        "ITSA2": "ITSA3",
        "ITSA4": "ITSA3",
        "TRPL3": "ISAE3",
        "LOGG3": "MRVE3",
    }
    df_nubank.replace(asset_map, inplace=True)

    # Load trading 212 transactions into dataframe
    try:
        with os.scandir(TRADING212_PATH) as entries:
            frames = []
            for entry in entries:
                if entry.is_file() and entry.name[-4:] == ".csv":

                    df = pd.read_csv(
                        entry,
                        header=0,
                        names=[
                            "transaction_type", "date", "notes",
                            "transaction_id", "total_value", "currency"
                        ],
                        parse_dates=[1],
                        date_format="ISO8601",
                    )

                    frames.append(df)

    except FileNotFoundError:
        print("There are no statement files from Trading 212.")
        return

    df_trading = pd.concat(frames)

    df_trading["asset_name"] = "Trading 212"
    df_trading["account_name"] = "TRADING 212"

    df_combined = (
        pd.concat([df_nubank, df_trading])
        .sort_values("date")
        .reset_index(drop=True)
    ).dropna(subset="total_value")

    transactions_map = {
        "Dividendo": "Dividend",
        "Dividendo - Transferido": "Dividend",
        "Juros Sobre Capital Próprio": "Dividend",
        "Juros Sobre Capital Próprio - Transferido": "Dividend",
        "Compra": "Purchase",
        "Cobrança de Taxa Semestral": "Bond Tax",
        "Resgate": "Sale",
        "Venda": "Sale",
        "Leilão de Fração": "Sale",
        "Transferência - Liquidação": "Transfer",
        "Debito": "Debit",
        "Credito": "Credit",
        "Withdrawal": "Sale",
        "Deposit": "Purchase"
    }
    df_combined.replace(transactions_map, inplace=True)

    # Replace purchase and sale of stocks
    df_combined.loc[
        (df_combined.cashflow == "Debit") & (
            df_combined.transaction_type == "Transfer"),
        "transaction_type"
    ] = "Sale"

    df_combined.loc[
        (df_combined.cashflow == "Credit") & (
            df_combined.transaction_type == "Transfer"),
        "transaction_type"
    ] = "Purchase"

    return df_combined


def include_accounts(conn):
    """
    Includes account.
    """

    df = fetch_transactions()

    for row in df.itertuples():

        account_name, currency = row[5], row[9]

        conn.execute(
            """
                INSERT INTO accounts (
                    account_name, currency
                )
                VALUES (?, ?)
                ON CONFLICT (account_name) DO NOTHING
                """,
            (account_name, currency)
        )

        conn.commit()


def include_assets(conn):
    """Include asset into assets database"""

    df = fetch_transactions()

    for row in df.itertuples():

        asset_name, account_name = row[4], row[5]

        if "TESOURO" in asset_name.upper():
            asset_type = "Bond"
        elif "FUNDO" in asset_name.upper():
            asset_type = "Mutual fund"
        elif "TRADING" in asset_name.upper():
            asset_type = "Cash ISA"
        else:
            asset_type = "Stock"

        positions_open = [
            "IVVB11", "CPLE3", "Tesouro IPCA+ 2026", "Tesouro Prefixado 2027",
            "Tesouro Selic 2028", "Tesouro IPCA+ 2035", "Trading 212"
        ]
        if asset_name in positions_open:
            position_open = 1
        else:
            position_open = 0

        purchase_date = df.groupby("asset_name").date.min().loc[asset_name]

        cursor = conn.cursor()

        account_id = cursor.execute(
            """
            SELECT account_id FROM accounts
            WHERE account_name == (?)
            """,
            (account_name,)
        ).fetchone()

        cursor.execute(
            """
            INSERT INTO assets (
                asset_name, asset_type, account_id,
                position_open, purchase_date
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (asset_name) DO NOTHING
            """,
            (
                asset_name, asset_type, account_id[0],
                position_open, purchase_date.strftime("%Y-%m-%d")

            )
        )

        cursor.close()
        conn.commit()


def include_bond_prices(conn):
    """
    Scrape "Tesouro Transparente" portal and updates daily prices from bonds
    in database.
    """

    url = (
        "https://www.tesourotransparente.gov.br/ckan/dataset/"
        "df56aa42-484a-4a59-8184-7676580c81e3/resource/"
        "796d2059-14e9-44e3-80c9-2d9e30b405c1/download/"
        "precotaxatesourodireto.csv"
    )

    r = requests.get(url)

    r.raise_for_status()

    n_lines = 0
    for line in r.iter_lines(decode_unicode=True):

        # Skip header
        if n_lines > 0:

            # Extract relevant data from response
            data = line.split(";")

            # Bond name is type + maturity year
            # e.g. "Tesouro Prefixado 2025"
            bond_name = data[0] + " " + data[1].split("/")[2]

            cursor = conn.cursor()

            # Fetch bond ID
            bond_id = cursor.execute(
                """
                    SELECT asset_id FROM assets
                    WHERE asset_name == (?)
                    """,
                (bond_name,)
            ).fetchone()

            if bond_id is not None:

                # Fetch purchase date for asset
                res = cursor.execute(
                    """
                    SELECT purchase_date FROM assets
                    WHERE asset_name == (?)
                    """,
                    (bond_name,)
                ).fetchone()

                purchase_date = dt.datetime.strptime(res[0], "%Y-%m-%d")

                bond_date = dt.datetime.strptime(
                    data[2], "%d/%m/%Y"
                )

                if bond_date >= purchase_date:

                    cursor.execute(
                        """
                        INSERT INTO prices (
                            date, asset_id, unit_price
                        )
                        VALUES (?, ?, ?)
                        ON CONFLICT (date, asset_id) DO NOTHING
                        """,
                        (
                            bond_date.date().isoformat(),
                            bond_id[0],
                            data[6].replace(",", ".")
                        )
                    )

                    conn.commit()

            cursor.close()

        n_lines += 1


def include_currencies(conn):
    """
    """

    data = yf.Ticker("GBPBRL=X").history(period="max")

    # Fetch purchase date for asset
    cursor = conn.cursor()
    min_date = cursor.execute(
        "SELECT date FROM transactions ORDER BY date"
    ).fetchone()
    cursor.close()

    purchase_date = dt.datetime.strptime(min_date[0], "%Y-%m-%d")

    price_dates = data.index.to_pydatetime()

    data = data[
        price_dates >= purchase_date.replace(tzinfo=ZoneInfo("Europe/London"))
    ]

    for row in data.itertuples():

        conn.execute(
            """
            INSERT INTO currencies (
                date, exchange_rate
            )
            VALUES (?, ?)
            ON CONFLICT (date) DO NOTHING
            """,
            (row[0].strftime("%Y-%m-%d"), row[4],)
        )

        conn.commit()


def include_stock_prices(conn):
    """
    Fetch prices from yfinance database.
    """

    cursor = conn.cursor()
    stocks = cursor.execute(
        """
        SELECT asset_name
        FROM assets
        WHERE asset_type == 'Stock'
        """
    ).fetchall()
    cursor.close()

    for stock in stocks:

        data = yf.Ticker(f"{stock[0]}.SA").history(
            period="max", auto_adjust=False
        )

        if not data.empty:

            cursor = conn.cursor()
            # Fetch purchase date for asset
            res = cursor.execute(
                """
                SELECT purchase_date
                FROM assets
                WHERE asset_name == (?)
                """,
                (stock[0],)
            ).fetchone()

            purchase_date = dt.datetime.strptime(res[0], "%Y-%m-%d")

            price_dates = data.index.to_pydatetime()

            prices = data[
                price_dates >= purchase_date.replace(
                    tzinfo=ZoneInfo("America/Sao_Paulo")
                )
            ]

            cursor = conn.cursor()
            asset_id = cursor.execute(
                """
                SELECT asset_id
                FROM assets
                WHERE asset_name == (?)
                """,
                (stock[0],)
            ).fetchone()

            cursor.close()

            for (index, row) in prices.iterrows():

                conn.execute(
                    """
                    INSERT INTO prices (
                        date, asset_id, unit_price
                    )
                    VALUES (?, ?, ?)
                    ON CONFLICT (date, asset_id) DO NOTHING
                    """,
                    (
                        index.strftime("%Y-%m-%d"),
                        asset_id[0],
                        row["Close"]
                    )
                )

                conn.commit()


def include_transactions(conn):
    """
    Insert a table for transactions into database.
    """

    df = fetch_transactions()

    for row in df.itertuples():

        cursor = conn.cursor()
        asset_id = cursor.execute(
            "SELECT asset_id FROM assets WHERE asset_name == (?)",
            (row[4],)
        ).fetchone()
        cursor.close()

        conn.execute(
            """
            INSERT INTO transactions (
                date, transaction_type, total_value, asset_id
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT (
                date, transaction_type, total_value, asset_id
            )
            DO NOTHING
            """,
            (
                row[2].to_pydatetime().date().isoformat(),
                row[3],
                abs(row[8]),
                asset_id[0]
            )
        )

        conn.commit()


def wants_to_create(name):
    """
    Returns true if user wants to update the database,
    false otherwise.
    """

    answer = ""
    while answer not in ["y", "n"]:
        answer = input(f"Do you want to create new {name}? (y/n) ").lower()
    if answer == "y":
        return True

    return False


if __name__ == "__main__":

    main()
