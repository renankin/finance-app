from finance_app.db import execute_db, query_db


def delete_asset(asset_id: int):
    """Delete asset."""

    execute_db("DELETE FROM assets WHERE asset_id = ?", (asset_id,))


def get_all_assets() -> list:
    """Fetch assets from all accounts and returns a list of dictionaries containing
    `asset_id`, `asset_name`, `account_name`, `asset_type` and `still_open`."""

    query = (
        "SELECT assets.asset_id, assets.asset_name, assets.asset_type,"
        " assets.still_open, accounts.account_name"
        " FROM assets"
        " JOIN accounts ON assets.account_id = accounts.account_id"
    )

    assets = query_db(query)

    if assets:
        return assets

    return []


def get_asset_by_id(asset_id: int) -> dict:
    """Fetch asset from database and returns a dictionary
    containing `account_id`, `account_name`, `asset_id`, `asset_name`, `asset_type` and
    `still_open`."""

    query = (
        "SELECT assets.asset_id, accounts.account_id, assets.asset_name,"
        " assets.asset_type, assets.still_open, accounts.account_name "
        " FROM assets"
        " JOIN accounts ON assets.account_id = accounts.account_id"
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


def insert_asset(account_id: int, asset_name: str, asset_type: str, still_open: int):
    """Insert into assets."""

    query = (
        "INSERT INTO assets (account_id, asset_name, asset_type, still_open)"
        " VALUES (?, ?, ?, ?)"
    )

    execute_db(query, (account_id, asset_name, asset_type, still_open))


def update_asset(
    asset_id: int, account_id: int, asset_name: str, asset_type: str, still_open: int
):
    """Update asset."""

    query = (
        "UPDATE assets"
        " SET asset_name = ?, account_id = ?, asset_type = ?, still_open = ?"
        " WHERE asset_id = ?"
    )

    execute_db(query, (asset_name, account_id, asset_type, still_open, asset_id))
