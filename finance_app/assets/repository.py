from finance_app.db import execute_db, query_db


def delete_asset(asset_id: int):
    """Delete asset."""

    execute_db("DELETE FROM assets WHERE asset_id = ?", (asset_id,))


def get_all_assets() -> list:
    """Fetch assets from all accounts and returns a list of dictionaries containing
    `asset_id`, `asset_name`, `account_name`, `source_display_name` and `still_open`."""

    query = (
        "SELECT assets.asset_id, assets.asset_name, "
        " market_sources.display_name AS source_display_name,"
        " assets.still_open, accounts.account_name"
        " FROM assets"
        " JOIN accounts ON assets.account_id = accounts.account_id"
        " JOIN market_sources ON assets.market_source_id = market_sources.source_id"
    )

    assets = query_db(query)

    if assets:
        return assets

    return []


def get_assets_from_source(source_id: int) -> list:
    """Fetches assets from database and returns a list of dictionaries containing `asset_id`."""

    query = "SELECT asset_id FROM assets WHERE market_source_id = ?"

    assets = query_db(query, (source_id,))

    if assets:
        return assets

    return []


def get_asset_by_id(asset_id: int) -> dict:
    """Fetch asset from database and returns a dictionary
    containing `account_id`, `account_name`, `asset_id`, `asset_name`,
    `source_display_name` `source_key` and `still_open`."""

    query = (
        "SELECT assets.asset_id, accounts.account_id, assets.asset_name,"
        " market_sources.display_name AS source_display_name, market_sources.source_key,"
        " assets.still_open, accounts.account_name"
        " FROM assets"
        " JOIN accounts ON assets.account_id = accounts.account_id"
        " JOIN market_sources ON assets.market_source_id = market_sources.source_id"
        " WHERE assets.asset_id = ?"
    )

    asset = query_db(query, (asset_id,), one=True)

    if asset:
        return asset

    return []


def get_assets_from_account(account_id: int) -> list:
    """Get all assets from a given account and returns a list of dictionaries
    containing `asset_id` and `asset_name` keys."""

    query = "SELECT asset_id, asset_name FROM assets WHERE account_id = ?"

    assets = query_db(query, (account_id,))

    if assets:
        return assets

    return []


def insert_asset(
    account_id: int, asset_name: str, market_source_id: int, still_open: int
):
    """Insert into assets."""

    query = (
        "INSERT INTO assets (account_id, asset_name, market_source_id, still_open)"
        " VALUES (?, ?, ?, ?)"
    )

    execute_db(query, (account_id, asset_name, market_source_id, still_open))


def update_asset(
    asset_id: int,
    account_id: int,
    asset_name: str,
    market_source_id: int,
    still_open: bool,
):
    """Update asset."""

    query = (
        "UPDATE assets"
        " SET asset_name = ?, account_id = ?, market_source_id = ?, still_open = ?"
        " WHERE asset_id = ?"
    )

    execute_db(query, (asset_name, account_id, market_source_id, still_open, asset_id))
