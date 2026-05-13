from finance_app.db import execute_db, query_db
from finance_app.market.fetchers import tesouro_fetcher, yfinance_fetcher
from finance_app.assets import repository as assets


def delete_dividends_for_asset(asset_id: int) -> bool:
    """Deletes dividends from database and returns True if successful"""

    dividends = get_dividends_for_asset(asset_id)

    if dividends:
        execute_db("DELETE FROM dividends WHERE asset_id = ?", (asset_id,))
        return True

    return False


def delete_prices_for_asset(asset_id: int) -> bool:
    """Deletes prices from database and returns True if successful."""

    prices = get_prices_for_asset(asset_id)

    if prices:
        execute_db("DELETE FROM prices WHERE asset_id = ?", (asset_id,))
        return True

    return False


def delete_splits_for_asset(asset_id: int) -> bool:
    """Deletes stock splits from database."""

    splits = get_splits_for_asset(asset_id)

    if splits:
        execute_db("DELETE FROM stock_splits WHERE asset_id = ?", (asset_id,))
        return True

    return False


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


def get_market_sources() -> list:
    """Fetch market sources from database and return a list of dictionaries with
    `source_name` keys."""

    query = "SELECT source_name FROM market_sources "

    sources = query_db(query)

    if sources:
        return sources

    return []


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


def get_splits_for_asset(asset_id: int) -> list:
    """Fetch splits from database and returns a list of dictionaries containing `date`
    and `split_ratio`."""

    query = (
        "SELECT date, split_ratio FROM stock_splits"
        " WHERE asset_id = ?"
        " ORDER BY date DESC"
    )

    splits = query_db(query, (asset_id,))

    if splits:
        return splits

    return []


def insert_dividends_for_asset(asset_id: int) -> bool:
    """Insert dividends for stock in database and returns True if successful"""

    asset = assets.get_asset_by_id(asset_id)

    if asset["asset_type"] == "stock":
        dividends = yfinance_fetcher.get_dividends(asset["asset_name"])

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


def insert_splits_for_asset(asset_id: int) -> bool:
    """Insert stock splits in database and returns True if successful."""

    asset = assets.get_asset_by_id(asset_id)

    if asset["asset_type"] == "stock":
        splits = yfinance_fetcher.get_splits(asset["asset_name"])

        if splits:
            args = []
            for split in splits:
                args.append((asset_id, split["date"], split["split_ratio"]))

            execute_db(
                "INSERT INTO stock_splits (asset_id, date, split_ratio)"
                " VALUES (?, ?, ?)"
                " ON CONFLICT (date, asset_id) DO NOTHING",
                args,
            )

            return True

    return False


def insert_prices_for_asset(asset_id: int) -> bool:
    """Insert prices for asset in database and returns True if successful."""

    asset = assets.get_asset_by_id(asset_id)

    if asset:
        if asset["asset_type"] != "bond":
            prices = yfinance_fetcher.get_prices(asset["asset_name"])
        else:
            prices = tesouro_fetcher.get_prices(asset["asset_name"])

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
