from finance_app.db import execute_db, query_db

from finance_app.assets import repository as assets


def get_prices_from_source(asset_name: str, source_name: str) -> dict:
    """Fetch prices from source if the source exists"""

    if source_name == "yfinance":
        from finance_app.market.fetchers import yfinance_fetcher

        return yfinance_fetcher.get_prices(asset_name)

    if source_name == "tesouro_website":
        from finance_app.market.fetchers import tesouro_fetcher

        return tesouro_fetcher.get_prices(asset_name)

    return {}


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

    prices = get_prices_from_source(asset["asset_name"], asset["source_name"])

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
