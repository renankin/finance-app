from finance_app.db import query_db, execute_db
from finance_app.market import market_stock_splits


def delete_transaction(transaction_id: int):
    """Deletes transaction."""

    execute_db("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))


def get_transactions_from_asset(asset_id: int) -> list[dict]:
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
        " WHERE assets.asset_id = ?"
        " ORDER BY transactions.date"
    )

    transactions = query_db(query, (asset_id,))

    if transactions:
        return transactions

    return []


def get_adjusted_transactions(asset_id: int) -> list:
    """Adjust cashflow for assets when there are stock splits and returns a list of
    dictionaries containing `date`, `shares`, `price`, `currency` and `adjusted`."""

    t = get_transactions_from_asset(asset_id)

    s = market_stock_splits.get_stock_splits(asset_id)

    for transaction in t:
        transaction["adjusted"] = "No"
        for split in s:
            if transaction["date"] <= split["date"]:
                transaction["shares"] *= split["split_ratio"]
                transaction["price"] /= split["split_ratio"]
                transaction["adjusted"] = "Yes"

    return t


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
