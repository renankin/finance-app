from finance_app.db import query_db, execute_db


def delete_transaction(transaction_id: int):
    """Deletes transaction."""

    execute_db("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))


def get_all_transactions() -> list:
    """Fetch all transactions from database and returns a list of dictionaries
    containing `transaction_id`, `account_name`, `asset_name`, `date`, `currency`,
    `shares` and `price`."""

    query = (
        "SELECT accounts.account_name, accounts.currency, assets.asset_name,"
        " transactions.transaction_id, transactions.date, transactions.shares, "
        " transactions.price"
        " FROM transactions"
        " JOIN assets ON transactions.asset_id = assets.asset_id"
        " JOIN accounts ON assets.account_id = accounts.account_id"
    )

    transactions = query_db(query)

    if transactions:
        return transactions

    return []


def get_transaction_by_id(transaction_id: int) -> dict:
    """Fetch transaction by id"""

    query = (
        "SELECT * FROM transactions"
        " JOIN assets ON transactions.asset_id = assets.asset_id"
        " JOIN accounts ON assets.account_id = accounts.account_id"
        " WHERE transactions.transaction_id = ?"
    )

    transaction = query_db(query, (transaction_id,), one=True)

    if transaction:
        return transaction

    return {}


def get_transactions_from_asset(asset_id: int) -> list:
    """Fetch all transactions of an asset and return as list of dictionaries
    with `date`, `price`, `shares` and `currency`."""

    query = (
        "SELECT transactions.date, transactions.shares, transactions.price,"
        " accounts.currency"
        " FROM transactions"
        " JOIN assets ON transactions.asset_id = assets.asset_id"
        " JOIN accounts ON assets.account_id = accounts.account_id"
        " WHERE transactions.asset_id = ?"
    )

    transactions = query_db(query, (asset_id,))

    if transactions:
        return transactions

    return []


def insert_transaction(asset_id: int, date: str, shares: float, price: float):
    """Inserts transaction in database."""

    query = (
        "INSERT INTO transactions (asset_id, date, price, shares) VALUES (?, ?, ?, ?)"
    )

    execute_db(query, (asset_id, date, price, shares))


def update_transaction(
    transaction_id: int, asset_id: int, date: str, shares: float, price: float
):
    """Updates transaction."""

    query = (
        "UPDATE transactions SET asset_id = ?, date = ?, shares = ?, price = ?"
        " WHERE transaction_id = ?"
    )

    execute_db(query, (asset_id, date, shares, price, transaction_id))
