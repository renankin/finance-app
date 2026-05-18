from finance_app.db import execute_db, query_db


def get_all_sources() -> list:
    """Fetch market sources from database and return a list of dictionaries with
    keys containing `display_name`, `source_id`, `supports_prices`, `source_key`,
    `supports_dividends` and `support_stock_splits`."""

    query = (
        "SELECT source_id, display_name, source_key, supports_prices,"
        " supports_dividends, supports_stock_splits"
        " FROM market_sources"
    )

    sources = query_db(query)

    if sources:
        return sources

    return []


def get_source_by_id(source_id: int) -> dict:
    """Fetch source from database and returns a dictionary with `display_name`, `source_key`,
    `supports_prices`, `supports_dividends` and `supports_stock_splits`"""

    query = (
        "SELECT source_id, display_name, source_key, supports_prices,"
        " supports_dividends, supports_stock_splits"
        " FROM market_sources WHERE source_id = ?"
    )

    source = query_db(query, (source_id,), one=True)

    if source:
        return source

    return {}


def update_source(
    source_id: int,
    display_name: str,
    source_key: str,
    supports_prices: bool,
    supports_dividends: bool,
    supports_splits: bool,
) -> bool:
    """Edits source and returns `True` if successful."""

    statement = (
        "UPDATE market_sources SET display_name = ?, source_key = ?,"
        " supports_dividends = ?, supports_prices = ?, supports_stock_splits = ? "
        " WHERE source_id = ?"
    )

    if get_source_by_id(source_id):
        execute_db(
            statement,
            (
                display_name,
                source_key,
                supports_dividends,
                supports_prices,
                supports_splits,
                source_id,
            ),
        )

        return True

    return False


def insert_source(
    display_name: str,
    source_key: str,
    supports_prices: bool,
    supports_dividends: bool,
    supports_stock_splits: bool,
) -> bool:
    """Insert new market source in database and returns `True` if successful."""

    statement = (
        "INSERT INTO market_sources"
        " (display_name, source_key, supports_prices, supports_dividends, supports_stock_splits)"
        " VALUES (?, ?, ?, ?, ?)"
    )

    execute_db(
        statement,
        (
            display_name,
            source_key,
            supports_prices,
            supports_dividends,
            supports_stock_splits,
        ),
    )

    return True


def delete_source(source_id: int) -> bool:
    """Delete source by id and return True if successful."""

    if get_source_by_id(source_id):
        execute_db("DELETE FROM market_sources WHERE source_id = ?", (source_id,))
        return True

    return False
