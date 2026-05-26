from finance_app.db import query_db, execute_db


def delete_transaction(transaction_id: int):
    """Deletes transaction."""

    execute_db("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))


def get_transactions_from_asset(account_id: int, asset_id: int) -> list[dict]:
    """Fetch all transactions from database and returns a list of dictionaries
    containing `currency`, `transaction_id`, `date`, `currency`,
    `shares` and `price`."""

    query = (
        "SELECT accounts.currency,"
        " transactions.transaction_id, transactions.date, transactions.shares, "
        " transactions.price"
        " FROM transactions"
        " JOIN assets ON transactions.asset_id = assets.asset_id"
        " JOIN accounts ON assets.account_id = accounts.account_id"
        " WHERE assets.asset_id = ? AND accounts.account_id = ?"
        " ORDER BY transactions.date"
    )

    transactions = query_db(query, (asset_id, account_id))

    if transactions:
        return transactions

    return []


def get_transaction_by_id(account_id: int, asset_id: int, transaction_id: int) -> dict:
    """Fetch transaction by id"""

    query = (
        "SELECT * FROM transactions"
        " JOIN assets ON transactions.asset_id = assets.asset_id"
        " JOIN accounts ON assets.account_id = accounts.account_id"
        " WHERE accounts.account_id = ? AND assets.asset_id = ? AND transactions.transaction_id = ?"
    )

    transaction = query_db(query, (account_id, asset_id, transaction_id), one=True)

    if transaction:
        return transaction

    return {}


def insert_transaction(asset_id: int, date: str, shares: float, price: float):
    """Inserts transaction in database."""

    query = (
        "INSERT INTO transactions (asset_id, date, price, shares) VALUES (?, ?, ?, ?)"
    )

    execute_db(query, (asset_id, date, price, shares))


def update_transaction(transaction_id: int, date: str, shares: float, price: float):
    """Updates transaction."""

    query = (
        "UPDATE transactions SET date = ?, shares = ?, price = ?"
        " WHERE transaction_id = ?"
    )

    execute_db(query, (date, shares, price, transaction_id))
