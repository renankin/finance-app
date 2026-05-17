from finance_app.db import execute_db, query_db
from finance_app.assets import repository as assets

from finance_app.market.fetchers.fetcher_registry import FetcherProtocol


def get_prices_for_asset(asset_id: int) -> list:
    """Get the prices for asset id and return them as list of dictionaries
    with `date`, `unit_price` and `currency` as keys."""

    query = (
        "SELECT prices.date, prices.unit_price, accounts.currency FROM prices"
        " JOIN accounts ON accounts.account_id = "
        " (SELECT account_id FROM assets WHERE asset_id = ?)"
        " WHERE prices.asset_id = ?"
        " ORDER BY prices.date DESC"
    )

    prices = query_db(query, (asset_id, asset_id))

    if prices:
        return prices

    return []


def delete_prices_for_asset(asset_id: int) -> bool:
    """Deletes prices from database and returns True if successful."""

    prices = get_prices_for_asset(asset_id)

    if prices:
        execute_db("DELETE FROM prices WHERE asset_id = ?", (asset_id,))
        return True

    return False


def insert_prices_for_asset(asset_id: int) -> bool:
    """Insert prices for asset in database and returns True if successful."""

    asset = assets.get_asset_by_id(asset_id)

    fetcher = FetcherProtocol(asset["source_name"])

    prices = fetcher.fetch_prices(asset["asset_name"])

    if prices:
        args = []
        for price in prices:
            args.append((asset_id, price["date"], price["price"]))

        execute_db(
            "INSERT INTO prices (asset_id, date, unit_price) VALUES (?, ?, ?)"
            " ON CONFLICT (date, asset_id) DO NOTHING",
            args,
        )

        return True

    return False
