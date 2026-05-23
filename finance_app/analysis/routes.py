from flask import Blueprint, flash, redirect, render_template, url_for

from finance_app.assets import repository as assets
from finance_app.analysis import repository as analysis
from finance_app.market import prices
from finance_app.transactions import repository as transactions

analysis_bp = Blueprint("analysis", __name__, template_folder="templates")


@analysis_bp.route("/analysis/return")
def show_return():
    """Displays the return on investiment for each asset own"""

    a = analysis.get_return_for_assets()

    if not a:
        flash("No assets to show. Must add asset first.")
        return redirect(url_for("assets.add"))

    return render_template("show_return.html", assets=a)


@analysis_bp.route("/analysis/dividends")
def get_dividends():
    """Fetch dividends."""

    a = assets.get_all_assets()

    if not a:
        flash("No assets to show. Must add asset first.")
        return redirect(url_for("assets.add"))

    return render_template("get_dividends_received.html", assets=a)


@analysis_bp.route("/analysis/dividends/<int:asset_id>")
def show_dividends(asset_id):
    """Show dividends received for asset."""

    dividends = analysis.get_dividends_received(asset_id)

    if not dividends:
        flash("No dividends to show.")
        return redirect(url_for("analysis.get_dividends"))

    return render_template("show_dividends_received.html", dividends=dividends)


@analysis_bp.route("/analysis/splits")
def get_splits():
    """Fetch splits."""

    a = assets.get_all_assets()

    if not a:
        flash("No assets to show. Must add asset first.")
        return redirect(url_for("assets.add"))

    return render_template("get_adjusted_transactions.html", assets=a)


@analysis_bp.route("/analysis/splits/<int:asset_id>")
def show_splits(asset_id):
    """Show adjusted prices and shares for asset."""

    t = analysis.get_adjusted_transactions(asset_id)

    return render_template("show_adjusted_transactions.html", transactions=t)
