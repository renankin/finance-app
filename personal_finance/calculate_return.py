#!/usr/bin/env python3

# Print the internal rate of return for each asset.

from datetime import datetime as dt
import numpy as np
import pandas as pd
from fetch_prices import fetch_stock_price, fetch_bond_price
from scipy import optimize
import sqlite3


def main():
    """
    Open transactions from database and calculate IRR.
    """

    conn = sqlite3.connect("transactions.db")

    irr = calculate_for_nubank(conn)

    irr.loc["Trading 212"] = calculate_for_trading212(conn)

    print(irr)

    conn.close()


def calculate_for_nubank(conn):
    """
    Calculates the IRR for Nubank.
    """

    df = pd.read_sql("SELECT * FROM nubank", conn, parse_dates="date")

    # Prepare dataframe for calculating IRR
    df.loc[df.transaction_type == "Purchase", "value"] *= -1
    
    # Calculate for assets
    irr = df.groupby("asset_name")[df.columns].apply(calculate_for_asset)

    # Calculate for portfolio
    df["elapsed_time"] = (df.date - df.date.min()).dt.days / 365.0
    irr["Total Nubank"] = compute_irr(df.value, df.elapsed_time)

    return irr


def calculate_for_asset(df):
    """
    Calculates the IRR for Nubank assets.
    """

    asset_name = df.asset_name.iloc[0]

    df["elapsed_time"] = (df.date - df.date.min()).dt.days / 365.0
    
    # Check if there's still quantity available
    total = (
        sum(df.quantity[df.transaction_type == "Purchase"])
        - sum(df.quantity[df.transaction_type == "Sale"]) 
    )
    if total > 0:
        if df.asset_type.unique() == "Stock":
            prices = fetch_stock_price(asset_name)
        if df.asset_type.unique() == "Bond":
            prices = fetch_bond_price(asset_name)

        # Append current valuation to dataframe
        elapsed_time = (dt.now() - df.date.min()).days / 365.0
    
        df.loc[len(df)] = [
            dt.now(), "Total", asset_name, "Stock", total,
            "BRL", total * prices.iloc[-1], elapsed_time
        ]

    return compute_irr(df.value, df.elapsed_time)


def calculate_for_trading212(conn):
    """
    Open dataframe from Trading 212 and calculates IRR.
    """

    df = pd.read_sql("SELECT * FROM trading_212", conn, parse_dates="date")

    total_value = df.value.sum()

    # Prepare dataframe for calculating IRR
    df.loc[
        (df.transaction_type == "Withdrawal")
        | (df.transaction_type == "Deposit"), "value"] *= -1

    df["elapsed_time"] = (df.date - df.date.min()).dt.days / 365.0

    # Append current valuation to dataframe
    elapsed_time = (dt.now() - df.date.min()).days / 365.0
    df.loc[len(df)] = [
        dt.now(), "Total", "Trading 212", total_value, "GBP", elapsed_time
    ]

    return compute_irr(df.value, df.elapsed_time)


def compute_irr(cashflow_values, elapsed_time, initial_guess=0):
    """
    Returns the internal rate of return (IRR).
    """

    # IRR is found when the sum of net present value equals 0
    solver = optimize.root(
        lambda irr: sum(cashflow_values / (1 + irr) ** elapsed_time),
        x0=initial_guess,
    )

    if not solver.success:
        print(solver.message)
        return np.nan

    return solver.x[0]


if __name__ == "__main__":
    main()
