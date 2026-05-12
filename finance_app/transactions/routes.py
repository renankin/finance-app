from flask import Blueprint, flash, redirect, render_template, request, url_for

from finance_app.accounts import repository as accounts
from finance_app.assets import repository as assets
from finance_app.transactions import repository as transactions


transactions_bp = Blueprint("transactions", __name__, template_folder="templates")


@transactions_bp.route("/transactions")
def index():
    """Shows a list of all transactions."""

    if not accounts.get_all_accounts():
        return redirect(url_for("accounts.index"))

    if not assets.get_all_assets():
        return redirect(url_for("assets.index"))

    t = transactions.get_all_transactions()

    if transactions:
        return render_template("transactions.html", transactions=t)

    flash("No transactions to show. Must add transaction first.")
    return redirect(url_for("transactions.add"))


@transactions_bp.route("/transactions/add", methods=["GET", "POST"])
def add():
    """Adds new transaction into database"""

    a = assets.get_all_assets()

    if not a:
        flash("No assets to show. Must add asset first.")
        return redirect(url_for("assets.add"))

    if request.method == "POST":
        asset_id = request.form.get("asset_id", type=int)
        date = request.form.get("date")
        shares = request.form.get("shares", type=float)
        price = request.form.get("price", type=float)

        transactions.insert_transaction(asset_id, date, shares, price)
        flash("Transaction added.")
        return redirect(url_for("transactions.index"))

    return render_template("add_transaction.html", assets=a)


@transactions_bp.route("/transactions/delete/<int:transaction_id>", methods=["POST"])
def delete(transaction_id):
    """Deletes transaction"""

    t = transactions.get_transaction_by_id(transaction_id)

    if t:
        transactions.delete_transaction(transaction_id)
        flash("Transaction deleted.")
    else:
        flash("Transaction not deleted.")

    return redirect(url_for("transactions.index"))


@transactions_bp.route(
    "/transactions/edit/<int:transaction_id>", methods=["GET", "POST"]
)
def edit(transaction_id):
    """Edit transaction"""

    t = transactions.get_transaction_by_id(transaction_id)

    if not t:
        flash("Transaction invalid.")
        return redirect(url_for("transactions.index"))

    if request.method == "POST":
        asset_id = request.form.get("asset_id", type=int)
        date = request.form.get("date")
        shares = request.form.get("shares", type=float)
        price = request.form.get("price", type=float)

        transactions.update_transaction(transaction_id, asset_id, date, shares, price)
        flash("Transaction updated.")
        return redirect(url_for("transactions.index"))

    return render_template("edit_transaction.html", transaction=t)
