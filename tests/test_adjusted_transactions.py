from datetime import date
from decimal import Decimal

from investment_analyser.transactions.service import (
    StockSplit,
    Transaction,
    adjust_transactions_for_splits,
)


def test_single_split():

    transactions = [
        Transaction(
            date=date(2024, 1, 31),
            shares=Decimal("10.00"),
            price=Decimal("100.00"),
        )
    ]

    stock_splits = [StockSplit(date=date(2025, 1, 31), split_ratio=Decimal("2.0"))]

    adjusted_transactions = [
        Transaction(
            date=date(2024, 1, 31),
            shares=Decimal("20.00"),
            price=Decimal("50.00"),
        )
    ]

    assert (
        adjust_transactions_for_splits(transactions, stock_splits)
        == adjusted_transactions
    )


def test_sequential_splits():

    transactions = [
        Transaction(
            date=date(2024, 1, 31),
            shares=Decimal("10.00"),
            price=Decimal("60.00"),
        )
    ]

    stock_splits = [
        StockSplit(date=date(2025, 1, 31), split_ratio=Decimal("2.0")),
        StockSplit(date=date(2026, 1, 31), split_ratio=Decimal("3.0")),
    ]

    adjusted_transactions = [
        Transaction(
            date=date(2024, 1, 31),
            shares=Decimal("60.00"),
            price=Decimal("10.00"),
        )
    ]

    assert (
        adjust_transactions_for_splits(transactions, stock_splits)
        == adjusted_transactions
    )


def test_multiple_transactions():

    transactions = [
        Transaction(
            date=date(2026, 1, 31),
            shares=Decimal("10.00"),
            price=Decimal("60.00"),
        ),
        Transaction(
            date=date(2023, 1, 31),
            shares=Decimal("5.00"),
            price=Decimal("10.00"),
        ),
    ]

    stock_splits = [
        StockSplit(date=date(2025, 1, 31), split_ratio=Decimal("2.0")),
        StockSplit(date=date(2022, 1, 31), split_ratio=Decimal("10.0")),
    ]

    adjusted_transactions = [
        Transaction(
            date=date(2026, 1, 31),
            shares=Decimal("10.00"),
            price=Decimal("60.00"),
        ),
        Transaction(
            date=date(2023, 1, 31),
            shares=Decimal("10.00"),
            price=Decimal("5.00"),
        ),
    ]

    assert (
        adjust_transactions_for_splits(transactions, stock_splits)
        == adjusted_transactions
    )


def test_split_same_date():

    transactions = [
        Transaction(
            date=date(2023, 1, 31), shares=Decimal("5.00"), price=Decimal("10.00")
        )
    ]

    stock_splits = [StockSplit(date=date(2023, 1, 31), split_ratio=Decimal("2.0"))]

    adjusted_transactions = [
        Transaction(
            date=date(2023, 1, 31), shares=Decimal("5.00"), price=Decimal("10.00")
        )
    ]

    assert (
        adjust_transactions_for_splits(transactions, stock_splits)
        == adjusted_transactions
    )


def test_empty_inputs():

    assert adjust_transactions_for_splits([], []) == []


def test_no_applicable_split():

    transactions = [
        Transaction(
            date=date(2024, 1, 31), shares=Decimal("10.00"), price=Decimal("100.00")
        )
    ]

    stock_splits = [
        StockSplit(date=date(2023, 1, 31), split_ratio=Decimal("2.0")),
        StockSplit(date=date(2022, 1, 31), split_ratio=Decimal("3.0")),
    ]

    adjusted_transactions = [
        Transaction(
            date=date(2024, 1, 31),
            shares=Decimal("10.00"),
            price=Decimal("100.00"),
        )
    ]

    assert (
        adjust_transactions_for_splits(transactions, stock_splits)
        == adjusted_transactions
    )


def test_decimal_precision():
    
    transactions = [
        Transaction(
            date=date(2024, 1, 31), shares=Decimal("10.53"), price=Decimal("10.20")
        )
    ]

    stock_splits = [StockSplit(date=date(2025, 1, 31), split_ratio=Decimal("2.5"))]

    adjusted_transactions = [
        Transaction(
            date=date(2024, 1, 31),
            shares=Decimal("26.325"),
            price=Decimal("4.08"),
        )
    ]

    assert (
        adjust_transactions_for_splits(transactions, stock_splits)
        == adjusted_transactions
    )
