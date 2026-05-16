from finance_app.db import execute_db, query_db
from finance_app.market.fetchers import yfinance_fetcher
from finance_app.assets import repository as assets


def get_splits_from_source(asset_name: str, source_name: str) -> dict:
    """Get stocks splits from source if it exists."""

    if source_name == "yfinance":
        from finance_app.market.fetchers import yfinance_fetcher

        return yfinance_fetcher.get_splits(asset_name)

    return {}


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


def delete_splits_for_asset(asset_id: int) -> bool:
    """Deletes stock splits from database."""

    splits = get_splits_for_asset(asset_id)

    if splits:
        execute_db("DELETE FROM stock_splits WHERE asset_id = ?", (asset_id,))
        return True

    return False


def insert_splits_for_asset(asset_id: int) -> bool:
    """Insert stock splits in database and returns True if successful."""

    asset = assets.get_asset_by_id(asset_id)

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
