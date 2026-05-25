from flask import Blueprint, flash, redirect, render_template, request, url_for

from finance_app.assets import repository as assets
from finance_app.transactions import repository as transactions


transactions_bp = Blueprint("transactions", __name__, template_folder="templates")


@transactions_bp.route("/transactions")
def index():
    """Get transactions."""

    a = assets.get_all_assets()

    return render_template("get_transactions.html", assets=a)


@transactions_bp.route("/transactions/<int:asset_id>/add", methods=["GET", "POST"])
def add(asset_id):
    """Adds new transaction into database."""

    a = assets.get_asset_by_id(asset_id)

    if request.method == "POST":
        date = request.form.get("date")
        shares = request.form.get("shares", type=float)
        price = request.form.get("price", type=float)

        transactions.insert_transaction(asset_id, date, shares, price)
        flash("Transaction added.")
        return redirect(url_for("transactions.show", asset_id=asset_id))

    return render_template("add_transaction.html", asset=a)


@transactions_bp.route("/transactions/<int:transaction_id>/delete", methods=["POST"])
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
    "/transactions/<int:transaction_id>/edit", methods=["GET", "POST"]
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
        return redirect(url_for("transactions.show", asset_id=asset_id))

    return render_template("edit_transaction.html", transaction=t)


@transactions_bp.route("/transactions/<int:asset_id>")
def show(asset_id):
    """Show transactions from asset as a table."""

    t = transactions.get_transactions_from_asset(asset_id)

    a = assets.get_asset_by_id(asset_id)

    return render_template("show_transactions.html", asset=a, transactions=t)
