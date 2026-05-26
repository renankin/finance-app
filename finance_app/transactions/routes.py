from flask import Blueprint, flash, redirect, render_template, request, url_for

from finance_app.accounts import repository as accounts
from finance_app.assets import repository as assets
from finance_app.transactions import repository as transactions


transactions_bp = Blueprint("transactions", __name__, template_folder="templates")


@transactions_bp.route("/acccounts/<int:account_id>/assets/<int:asset_id>/transactions")
def show_transactions(account_id, asset_id):
    """Show transactions from asset as a table."""

    trans = transactions.get_transactions_from_asset(account_id, asset_id)

    if not trans:
        flash("No transactions to show. Must add new transaction first.")
        return redirect(
            url_for(
                "transactions.add_transaction", account_id=account_id, asset_id=asset_id
            )
        )

    account = accounts.get_account_by_id(account_id)

    asset = assets.get_asset_by_id(account_id, asset_id)

    return render_template(
        "show_transactions.html", account=account, asset=asset, transactions=trans
    )


@transactions_bp.route(
    "/accounts/<int:account_id>/assets/<int:asset_id>/transactions/add",
    methods=["GET", "POST"],
)
def add_transaction(account_id, asset_id):
    """Adds new transaction into database."""

    account = accounts.get_account_by_id(account_id)

    asset = assets.get_asset_by_id(account_id, asset_id)

    if request.method == "POST":
        date = request.form.get("date")
        shares = request.form.get("shares", type=float)
        price = request.form.get("price", type=float)

        transactions.insert_transaction(asset_id, date, shares, price)
        flash("Transaction added.")
        return redirect(
            url_for(
                "transactions.show_transactions",
                account_id=account_id,
                asset_id=asset_id,
            )
        )

    return render_template("add_transaction.html", account=account, asset=asset)


@transactions_bp.route(
    "/accounts/<int:account_id>/assets/<int:asset_id>/transactions/<int:transaction_id>/delete",
    methods=["POST"],
)
def delete_transaction(account_id, asset_id, transaction_id):
    """Deletes transaction"""

    transaction = transactions.get_transaction_by_id(
        account_id, asset_id, transaction_id
    )

    if transaction:
        transactions.delete_transaction(transaction_id)
        flash("Transaction deleted.")
    else:
        flash("Transaction not deleted.")

    return redirect(
        url_for(
            "transactions.show_transactions", account_id=account_id, asset_id=asset_id
        )
    )


@transactions_bp.route(
    "/accounts/<int:account_id>/assets/<int:asset_id>/transactions/<int:transaction_id>/edit",
    methods=["GET", "POST"],
)
def edit_transaction(account_id, asset_id, transaction_id):
    """Edit transaction"""

    account = accounts.get_account_by_id(account_id)

    asset = assets.get_asset_by_id(account_id, asset_id)

    transaction = transactions.get_transaction_by_id(
        account_id, asset_id, transaction_id
    )

    if request.method == "POST":
        date = request.form.get("date")
        shares = request.form.get("shares", type=float)
        price = request.form.get("price", type=float)

        transactions.update_transaction(transaction_id, date, shares, price)
        flash("Transaction updated.")
        return redirect(
            url_for(
                "transactions.show_transactions",
                account_id=account_id,
                asset_id=asset_id,
            )
        )

    return render_template(
        "edit_transaction.html", account=account, asset=asset, transaction=transaction
    )
