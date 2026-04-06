from flask import Blueprint, flash, redirect, render_template, request, url_for

from finance_app.transactions.helpers import get_form_params
from finance_app.db import query_db, insert_db
from finance_app.stocks.helpers import lookup_stock, get_transactions


MIN_SHARES = 10

bp = Blueprint("transactions", __name__, template_folder="templates")


@bp.route("/")
def index():
    """Display shares currently in balance"""

    accounts = query_db("SELECT DISTINCT(currency) FROM transactions")

    for account in accounts:
        symbols = query_db(
            "SELECT DISTINCT(symbol) FROM transactions WHERE currency = ?",
            [account["currency"]],
        )

        symbols = [row["symbol"] for row in symbols]

        total_account = 0
        assets = []
        for symbol in symbols:
            asset = {"symbol": symbol}

            transactions = get_transactions(symbol)

            asset["shares"] = sum(t["adj_shares"] for t in transactions)

            if asset["shares"] > MIN_SHARES:
                asset["price"] = lookup_stock(symbol)["currentPrice"]
                asset["total"] = asset["price"] * asset["shares"]
                total_account += asset["total"]
                assets.append(asset)

        account["assets"] = assets
        account["total"] = total_account

    return render_template("index.html", accounts=accounts)


@bp.route("/<int:id>/delete", methods=["POST"])
def delete(id):
    """Deletes transaction"""

    symbol = query_db("SELECT symbol FROM transactions WHERE id = ?", [id], one=True)[
        "symbol"
    ]

    insert_db("DELETE FROM transactions WHERE id = ?", [id])

    return render_template(
        "transactions.html", transactions=get_transactions(symbol)
    )


@bp.route("/<int:id>/edit", methods=["GET", "POST"])
def edit(id):
    """Edit transaction"""

    row = query_db("SELECT * FROM transactions WHERE id == ?", [id], one=True)

    if request.method == "POST":
        form = get_form_params(
            date=request.form.get("date"),
            shares=request.form.get("shares"),
            price=request.form.get("price"),
        )

        if not form:
            return redirect(url_for("edit", id=id))
        else:
            insert_db(
                "UPDATE transactions SET date = ?, shares = ?, price = ? WHERE id = ?",
                [
                    form["date"],
                    form["shares"],
                    form["price"],
                    id,
                ],
            )

        return render_template(
            "transactions.html", transactions=get_transactions(row["symbol"])
        )

    return render_template("edit.html", transaction=row)


@bp.route("/history", methods=["GET", "POST"])
def history():
    """Shows history of transactions"""

    symbols = query_db("SELECT DISTINCT(symbol) FROM transactions ORDER BY symbol DESC")

    symbols = [s["symbol"] for s in symbols]

    if request.method == "POST":
        symbol = request.form.get("symbol")

        if symbol not in symbols:
            flash("Invalid symbol")
            return url_for("history")

        return render_template(
            "transactions.html", transactions=get_transactions(symbol)
        )

    return render_template("find_transactions.html", symbols=symbols)
