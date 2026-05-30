from finance_app.db import execute_db, query_db
from finance_app.assets import assets as assets
from finance_app.market import market_sources

from finance_app.market.fetchers.fetcher_registry import FetcherProtocol

def get_stock_splits(asset_id: int) -> list:
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


def delete_stock_splits(asset_id: int) -> bool:
    """Deletes stock splits from database."""

    splits = get_stock_splits(asset_id)

    if splits:
        execute_db("DELETE FROM stock_splits WHERE asset_id = ?", (asset_id,))
        return True

    return False


def insert_stock_splits(asset_id: int) -> bool:
    """Insert stock splits in database and returns True if successful."""

    asset = assets.get_asset_by_id(asset_id)

    market_source = market_sources.get_source_by_id(asset["market_source_id"])

    fetcher = FetcherProtocol(market_source)

    splits = fetcher.fetch_stock_splits(asset["asset_name"])

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
