#!/usr/bin/env python3

# Print the internal rate of return for each asset.

import datetime as dt
import pandas as pd
from scipy import optimize
import sqlite3

DB_NAME = "transactions.db"


def main():
    """
    Opens SQL database and calculate the rate of return.
    """

    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()

    currency = ""
    while currency not in ["GBP", "BRL"]:
        currency = input("Select currency (GBP/BRL): ").upper()

    all_cashflows = pd.DataFrame()

    assets = cursor.execute("SELECT asset_name FROM assets").fetchall()
    for asset_name in assets:

        asset_info = cursor.execute(
            "SELECT * FROM assets WHERE asset_name == (?)",
            (asset_name[0],)
        ).fetchone()

        asset_id, purchase_date, position_open = (
            asset_info[0], pd.to_datetime(asset_info[2]), asset_info[5]
        )

        transactions = pd.read_sql(
            "SELECT * FROM transactions WHERE asset_id == (?) ORDER BY date",
            db,
            parse_dates=["date"],
            params=(asset_id,)
        )

        prices = pd.read_sql(
            "SELECT * FROM prices WHERE asset_id == (?) ORDER BY date",
            db,
            parse_dates=["date"],
            params=(asset_id,)
        )

        cashflow = get_cashflow(transactions, prices, position_open)

        asset_currency = cursor.execute(
            """
            SELECT currency FROM accounts
            WHERE account_id == (
                SELECT account_id
                FROM assets
                WHERE asset_id == (?)
            )
            """,
            (asset_id,)
        ).fetchone()

        if currency != asset_currency[0]:

            data = pd.read_sql(
                "SELECT * FROM currencies",
                db,
                parse_dates="date",
            )

            cashflow = exchange_currency(cashflow, data, currency)

        elapsed_time = (cashflow.date - purchase_date).dt.days / 365.0

        irr = compute_irr(cashflow.total_value, elapsed_time)

        print(asset_name[0], irr)

        all_cashflows = pd.concat([all_cashflows, cashflow])

    min_date = cursor.execute(
        """
        SELECT date
        FROM transactions
        ORDER BY date
        """
    ).fetchone()

    elapsed_time = (
        all_cashflows.date - pd.to_datetime(min_date[0])
    ).dt.days / 365.0

    irr = compute_irr(all_cashflows.total_value, elapsed_time)

    print("Total", irr)


def get_cashflow(transactions, prices, position_open):
    """
    Takes transactions and prices dataframe
    and returns the IRR for the asset.
    """

    cashflow = pd.DataFrame()

    cashflow["date"] = transactions.date
    cashflow["total_value"] = transactions.total_value.where(
        transactions.transaction_type != "Purchase",
        -transactions.total_value
    )

    # Situation for Trading 212
    if position_open and prices.empty:

        balance = transactions.total_value.where(
            transactions.transaction_type != "Sale",
            -transactions.total_value
        ).sum()

        cashflow.loc[len(cashflow)] = [transactions.date.max(), balance]

    # Stocks and bonds in Nubank
    if position_open and not prices.empty:
    
        trades = transactions[
            transactions.transaction_type.isin(["Purchase", "Sale"])
        ].copy()
        trades = trades.merge(
            prices[["date", "unit_price"]],
            on="date",
            how="left"
        )
        trades["quantity"] = trades.total_value / trades.unit_price
        trades.loc[trades.transaction_type == "Sale", "quantity"] *= -1
        
        today = dt.datetime.now()
        valuation = trades.quantity.sum() * prices.unit_price.iloc[-1]
        cashflow.loc[len(cashflow)] = [today, valuation]

    return cashflow


def compute_irr(cashflow_values, elapsed_time, initial_guess=0):
    """
    Returns the internal rate of return (IRR) based on a cashflow dataframe
    which constains the total value of transactions and the elapsed time.
    """

    # IRR is found when the sum of net present value equals 0
    solver = optimize.root(
        lambda irr: sum(cashflow_values / (1 + irr) ** elapsed_time),
        x0=initial_guess,
    )

    if not solver.success:
        print(solver.message)
        return None

    return solver.x[0]


def exchange_currency(df, currency_df, target_currency):
    """
    Insert the dataframe which constains transactions dates and values and 
    exchange the currency.
    """

    currency_df = currency_df[currency_df.date >= df.date.min()]

    currency_df = currency_df.set_index("date")
    df = df.set_index("date")
    currency_df = currency_df.reindex(df.index, method="ffill")

    if target_currency == "GBP":
        currency_df.exchange_rate = 1 / currency_df.exchange_rate

    df.total_value *= currency_df.exchange_rate

    return df.reset_index()


if __name__ == "__main__":
    main()
