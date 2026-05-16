from finance_app.db import execute_db, query_db
from finance_app.assets import repository as assets


def get_dividends_from_source(asset_name: str, source_name: str) -> dict:
    """Get divindeds from source if it exists."""

    if source_name == "yfinance":
        from finance_app.market.fetchers import yfinance_fetcher

        return yfinance_fetcher.get_dividends(asset_name)

    return {}


def get_dividends_for_asset(asset_id: int) -> list:
    """Fetch dividends from database and return them as a list of dictionaries
    containing "date" and "dividend_value" keys."""

    query = (
        "SELECT * FROM dividends"
        " JOIN assets ON assets.asset_id = dividends.asset_id"
        " JOIN accounts ON accounts.account_id = assets.account_id"
        " WHERE dividends.asset_id = ?"
        " ORDER BY dividends.date DESC"
    )

    divs = query_db(query, (asset_id,))

    if divs:
        return divs

    return []


def delete_dividends_for_asset(asset_id: int) -> bool:
    """Deletes dividends from database and returns True if successful"""

    dividends = get_dividends_for_asset(asset_id)

    if dividends:
        execute_db("DELETE FROM dividends WHERE asset_id = ?", (asset_id,))
        return True

    return False


def insert_dividends_for_asset(asset_id: int) -> bool:
    """Insert dividends for stock in database and returns True if successful."""

    a = assets.get_asset_by_id(asset_id)

    dividends = get_dividends_from_source(a["asset_name"], a["source_name"])

    if dividends:
        args = []
        for div in dividends:
            args.append((asset_id, div["date"], div["dividend"]))

        execute_db(
            "INSERT INTO dividends (asset_id, date, dividend_value)"
            " VALUES (?, ?, ?)"
            " ON CONFLICT (date, asset_id) DO NOTHING",
            args,
        )

        return True

    return False
