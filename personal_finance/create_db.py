#!/usr/bin/env python3

# Create a SQLite database with transactions from Nubank and Trading 212

import csv
from datetime import datetime
from dotenv import load_dotenv
import os
import sqlite3
import yfinance as yf

load_dotenv()

DB_NAME = "transactions.db"
NUBANK_PATH = os.environ.get("PATH_TO_NUBANK")
TRADING212_PATH = os.environ.get("PATH_TO_TRADING212")


def main():
    """
    Initialises a database with transactions from Nubank and Trading 212.
    """

    db = sqlite3.connect(DB_NAME)

    cursor = db.cursor()

    include_nubank_table(cursor)
    include_trading212_table(cursor)

    db.commit()


def include_nubank_table(cursor):
    """
    Insert a table for Nubank transactions into database.
    """

    # Delete table if it exists and create a new one
    cursor.execute("DROP TABLE IF EXISTS nubank")
    cursor.execute(
        """
        CREATE TABLE nubank (
            date DATE NOT NULL,
            transaction_type VARCHAR(50) NOT NULL,
            asset_name VARCHAR(50) NOT NULL,
            asset_type VARCHAR(25) NOT NULL,
            quantity FLOAT NOT NULL,
            currency CHAR(3) NOT NULL,
            value REAL NOT NULL
        )
        """
    )

    # Dicts for splits and transactions
    name_change = {
        "TRPL3": "ISAE3",
        "ITSA4": "ITSA3",
        "LOGG3": "MRVE3",
        }
    splits = {}
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
    }

    # Include entries for Nubank
    entries = os.scandir(NUBANK_PATH)
    for entry in entries:

        if entry.name[-4:] == ".csv":
            file = open(f"{NUBANK_PATH}/{entry.name}", "r")
            reader = csv.DictReader(
                file,
                fieldnames=[
                    "Entrada/Saída", "Data", "Movimentação", "Produto",
                    "Instituição", "Quantidade", "Preço unitário",
                    "Valor da Operação"
                ],
            )
            next(reader)

            for row in reader:
                value = (
                    row["Valor da Operação"].replace("R$", "")
                    .replace(",", "").strip()
                )

                if "-" not in value:

                    value = float(value)

                    # Edge cases
                    if row["Entrada/Saída"] == "Credito":
                        transactions_map["Transferência"] = "Purchase"
                        transactions_map[
                            "Transferência - Liquidação"
                        ] = "Purchase"
                    else:
                        transactions_map["Transferência"] = "Sale"
                        transactions_map[
                            "Transferência - Liquidação"
                        ] = "Sale"

                    date = (
                        datetime.strptime(row["Data"], "%d/%m/%Y")
                        .date().isoformat()
                    )
                    
                    transaction_type = transactions_map[row["Movimentação"]]
                    
                    asset_name = row["Produto"].split(" - ")[0].strip()
                    if asset_name in name_change:
                        asset_name = name_change[asset_name]

                    if "TESOURO" in asset_name.upper():
                        asset_type = "Bond"
                    elif "FUNDO" in asset_name.upper():
                        asset_type = "Mutual fund"
                    else:
                        asset_type = "Stock"

                    # Adjust quantity based on stock splits
                    qty = float(row["Quantidade"])
                    if asset_type == "Stock":
                        if asset_name in splits:
                            if not splits[asset_name].empty:
                                valid_splits = splits[asset_name][
                                    splits[asset_name].index > date
                                ]
                                for split in valid_splits:
                                    qty *= split
                        else:
                            try:
                                data = yf.Ticker(f"{asset_name}.SA").splits
                            except:
                                print(
                                    "Failed to connect to yfinance. Not adjusting for stock splits..."
                                )
                            else:
                                splits[asset_name] = data

                    # Insert transaction into database
                    cursor.execute(
                        """
                        INSERT INTO nubank
                        (date, transaction_type, asset_name,
                        asset_type, quantity, currency, value)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (date, transaction_type, asset_name,
                         asset_type, qty, "BRL", value)
                    )


def include_trading212_table(cursor):
    """
    Insert table in the database with transactions from Trading 212.
    """

    # Delete table if it exists and create a new one
    cursor.execute("DROP TABLE IF EXISTS trading_212")
    cursor.execute(
        """
        CREATE TABLE trading_212 (
            date DATETIME NOT NULL,
            transaction_type VARCHAR(50) NOT NULL,
            asset_name VARCHAR(50) NOT NULL,
            value REAL NOT NULL,
            currency CHAR(3) NOT NULL
        )
        """
    )

    # Include entries for trading 212
    entries = os.scandir(TRADING212_PATH)
    for entry in entries:

        # Capture only CSV files
        if entry.name[-4:] == ".csv":

            # Open CSV files
            file = open(f"{TRADING212_PATH}/{entry.name}", "r")
            reader = csv.DictReader(
                file,
                fieldnames=[
                    "Action", "Time", "Notes", "ID",
                    "Total", "Currency"
                ],
            )

            # Skip header
            next(reader)

            # Iterate over CSV files
            for row in reader:

                # Insert transaction into database
                cursor.execute(
                    """
                    INSERT INTO trading_212
                    (date, transaction_type, asset_name, value, currency)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        row["Time"].split(".")[0],
                        row["Action"], "Trading 212",
                        row["Total"], row["Currency"]
                    )
                )


if __name__ == "__main__":

    main()
