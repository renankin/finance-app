from finance_app.db import execute_db, query_db
from finance_app.assets import assets as assets
from finance_app.market import sources

from finance_app.market.fetchers.fetcher_registry import FetcherProtocol


def get_dividends_for_asset(asset_id: int) -> list:
    """Fetch dividends from database and return them as a list of dictionaries
    containing `date`, `dividend_value` and `currency` keys."""

    query = (
        "SELECT dividends.date, dividends.dividend_value, accounts.currency FROM dividends"
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

    
    asset = assets.get_asset_by_id(asset_id)

    market_source = sources.get_source_by_id(asset["market_source_id"])

    fetcher = FetcherProtocol(market_source)

    dividends = fetcher.fetch_dividends(asset["asset_name"])

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
