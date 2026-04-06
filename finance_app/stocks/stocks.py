from flask import Blueprint, flash, redirect, request, render_template, url_for

from finance_app.db import insert_db, query_db
from finance_app.stocks.helpers import lookup_stock, get_dividends, get_hist_prices
from finance_app.transactions.helpers import get_form_params


bp = Blueprint("stocks", __name__, template_folder="templates")


@bp.route("/add", methods=["GET", "POST"])
def add():
    """Adds new stock from yfinance into transactions database"""

    if request.method == "POST":
        form = get_form_params(
            date=request.form.get("date"),
            shares=request.form.get("shares"),
            price=request.form.get("price"),
            symbol=request.form.get("symbol"),
        )

        if not form:
            return redirect(url_for("stocks.add"))

        # Check if price is within daily range
        prices = get_hist_prices(form["symbol"], form["date"])

        if not prices:
            flash("Price not found.")
            return redirect(url_for("stocks.add"))

        if prices["low"] == 0 or prices["high"] == 0:
            flash("Price open or high return 0 on that date")
            return redirect(url_for("stocks.add"))

        # Adjust stock splits
        info = lookup_stock(form["symbol"])

        if not info:
            flash("Symbol does not exist or may be delisted.")
            return redirect(url_for("stocks.add"))

        if info["splits"]:
            shares = form["shares"]
            price = form["price"]

            for split in info["splits"]:
                if form["date"] <= split["date"]:
                    shares *= split["ratio"]
                    price /= split["ratio"]
                    prices["low"] *= split["ratio"]
                    prices["high"] *= split["ratio"]

            if price >= prices["high"] or price <= prices["low"]:
                flash(
                    f"Expected price: {info['currency']}"
                    f" {prices['low']:.2f} - {prices['high']:.2f}."
                )

        insert_db(
            "INSERT INTO transactions (date, symbol, shares, price, currency)"
            " VALUES (?, ?, ?, ?, ?)",
            [
                prices["date"],
                form["symbol"],
                form["shares"],
                form["price"],
                prices["currency"],
            ],
        )

        flash("Symbol purchased.")

    return render_template("add.html")


@bp.route("/dividends", methods=["GET", "POST"])
def dividends():
    """Displays the dividends for each stock"""

    rows = query_db("SELECT DISTINCT(symbol) FROM transactions")
    symbols = [row["symbol"] for row in rows]

    if request.method == "POST":
        symbol = request.form.get("symbol")

        if symbol not in symbols:
            flash("Invalid symbol.")
            return redirect(url_for("stocks.dividends"))

        dividends = get_dividends(symbol)

        if not dividends:
            flash("No dividend history available.")
            return redirect(url_for("stocks.dividends"))

        currency = query_db(
            "SELECT DISTINCT(currency) FROM transactions WHERE symbol = ?",
            [symbol],
            one=True,
        )["currency"]

        return render_template(
            "dividends.html",
            dividends=dividends,
            currency=currency,
            total=sum(dividends["values"]),
        )

    return render_template("find_dividends.html", symbols=symbols)


@bp.route("/search", methods=["GET", "POST"])
def search():
    """Searchs for stock in yfinance"""

    if request.method == "POST":
        symbol = request.form.get("symbol")

        if not symbol:
            flash("Must provide symbol.")
            return redirect(url_for("stocks.search"))

        quote = lookup_stock(symbol)

        if not quote:
            flash("Price not found.")
            return redirect(url_for("stocks.search"))

        return render_template("searched.html", quote=quote)

    return render_template("search.html")
