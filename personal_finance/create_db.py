#!/usr/bin/env python3

# Create a SQLite database with transactions from Nubank and Trading 212

import csv
from datetime import datetime
from dotenv import load_dotenv
import os
import sqlite3

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
            type VARCHAR(50) NOT NULL,
            name VARCHAR(50) NOT NULL,
            quantity FLOAT NOT NULL,
            value REAL NOT NULL
        )
        """
    )

    # Include entries for Nubank
    entries = os.scandir(NUBANK_PATH)
    for entry in entries:

        # Capture only CSV files
        if entry.name[-4:] == ".csv":

            # Open CSV files
            file = open(f"{NUBANK_PATH}/{entry.name}", "r")
            reader = csv.DictReader(
                file,
                fieldnames=[
                    "Entrada/Saída", "Data", "Movimentação", "Produto",
                    "Instituição", "Quantidade", "Preço unitário",
                    "Valor da Operação"
                ],
            )

            # Skip header
            next(reader)

            # Iterate over CSV lines
            for row in reader:

                # Extract operation value
                value = (
                    row["Valor da Operação"].replace("R$", "")
                    .replace(",", "").strip()
                )

                # Check if there's a value in the transaction
                if "-" not in value:

                    # Define type of transaction dict
                    transactions = {
                        "Dividendo": "Dividend",
                        "Dividendo - Transferido": "Dividend",
                        "Juros Sobre Capital Próprio": "Dividend",
                        "Juros Sobre Capital Próprio - Transferido":
                        "Dividend",
                        "Compra": "Purchase",
                        "Cobrança de Taxa Semestral": "Bond Tax",
                        "Resgate": "Sale",
                        "Venda": "Sale",
                        "Leilão de Fração": "Sale",
                    }

                    # Edge cases for purchase and sale of stocks
                    if row["Entrada/Saída"] == "Credito":
                        transactions["Transferência"] = "Purchase"
                        transactions["Transferência - Liquidação"] = "Purchase"
                    else:
                        transactions["Transferência"] = "Sale"
                        transactions["Transferência - Liquidação"] = "Sale"

                    # Extract remaining operations
                    date = (
                        datetime.strptime(row["Data"], "%d/%m/%Y")
                        .date().isoformat()
                    )
                    type = transactions[row["Movimentação"]]
                    name = row["Produto"].split(" - ")[0].strip()
                    qty = row["Quantidade"]

                    # Insert transaction into database
                    cursor.execute(
                        """
                        INSERT INTO nubank (date, type, name, quantity, value)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (date, type, name, qty, value)
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
            type VARCHAR(50) NOT NULL,
            name VARCHAR(50) NOT NULL,
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
                    INSERT INTO trading_212 (date, type, name, value, currency)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (row["Time"], row["Action"], "Trading 212",
                     row["Total"], row["Currency"])
                )



if __name__ == "__main__":

    main()
