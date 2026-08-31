from datetime import date
from decimal import Decimal
from typing import TypedDict

from investment_analyser.market_data.repository.stock_splits import get_stock_splits


class Transaction(TypedDict):
    date: date
    shares: Decimal
    price: Decimal


class StockSplit(TypedDict):
    date: date
    split_ratio: Decimal


def get_split_adjusted_transactions(transactions: list[dict]) -> list[dict]:
    """Adjust cashflow for assets when there are stock splits.

    The transactions must contain `date`, `shares` and `price` keys.

    The returned list of dictionaries will contain the same keys as the input `transactions`
    in addition to `is_adjusted` keys.
    """

    adj_transactions = []
    for transaction in transactions:
        adj_transaction = transaction

        adj_transaction["is_adjusted"] = False
    
        for split in get_stock_splits(transaction["asset_id"]):
            if transaction["date"] <= split["date"]:
                adj_transaction["shares"] *= split["split_ratio"]
                adj_transaction["price"] /= split["split_ratio"]
                adj_transaction["is_adjusted"] = True

        adj_transactions.append(adj_transaction)

    return adj_transactions


def adjust_transactions_for_splits(
    transactions: list[Transaction], splits: list[StockSplit]
) -> list[Transaction]:
    """Adjust transactions for stock splits occurring after each transaction date."""

    adj_transactions = []
    for transaction in transactions:
        adj_transaction: Transaction = {
            "date": transaction["date"],
            "shares": transaction["shares"],
            "price": transaction["price"],
        }

        for split in splits:
            if transaction["date"] < split["date"]:
                adj_transaction["shares"] *= split["split_ratio"]
                adj_transaction["price"] /= split["split_ratio"]

        adj_transactions.append(adj_transaction)

    return adj_transactions
