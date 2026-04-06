import datetime as dt
from flask import Blueprint, render_template

from finance_app.db import query_db
from finance_app.stocks.helpers import lookup_stock, get_dividends, get_transactions
from finance_app.roi.helpers import compute_irr

MIN_SHARES = 10

bp = Blueprint("roi", __name__, template_folder="templates")


@bp.route("/roi")
def roi():
    """Displays the return on investiment for each asset own"""

    assets = query_db("SELECT DISTINCT(symbol), currency FROM transactions")

    for asset in assets:
        transactions = get_transactions(asset["symbol"])

        # Calculate IRR
        cashflow = [
            -1 * transaction["adj_price"] * transaction["adj_shares"]
            for transaction in transactions
        ]

        dates = [transaction["date"] for transaction in transactions]

        dividends = get_dividends(asset["symbol"])
        if dividends:
            cashflow += dividends["values"]
            dates += dividends["dates"]

        total_shares = sum(t["adj_shares"] for t in transactions)

        if total_shares > MIN_SHARES:
            quote = lookup_stock(asset["symbol"])
            cashflow.append(quote["currentPrice"] * total_shares)
            dates.append(dt.datetime.now().date())

        elapsed_years = [(date - min(dates)).days / 365 for date in dates]

        asset["holding_period"] = (dt.datetime.now().date() - min(dates)).days

        if asset["holding_period"] < 365:
            asset["annual_return"] = None
        else:
            asset["annual_return"] = compute_irr(cashflow, elapsed_years)

        # Calculate absolute return
        asset["total_earned"] = sum(val for val in cashflow if val > 0)
        asset["total_invested"] = sum(abs(val) for val in cashflow if val < 0)
        asset["absolute_return"] = (
            asset["total_earned"] - asset["total_invested"]
        ) / asset["total_invested"]

    return render_template("return.html", assets=assets)
