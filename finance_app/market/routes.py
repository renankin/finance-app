from flask import Blueprint, flash, redirect, request, render_template, url_for

from finance_app.assets import repository as assets
from finance_app.market import repository as market

market_bp = Blueprint("market", __name__, template_folder="templates")


@market_bp.route("/market")
def index():
    """Defines sources for market."""

    s = market.get_market_sources()

    return render_template("market_sources.html", market_sources=s)


@market_bp.route("/market/add/", methods=["GET", "POST"])
def add():
    """Add new source."""

    if request.method == "POST":
        source_name = request.form.get("source_name")
        p = request.form.get("supports_prices", type=bool)
        d = request.form.get("supports_dividends", type=bool)
        s = request.form.get("supports_stocks_splits", type=bool)

        market.insert_market_source(source_name, p, d, s)
        flash("Source added.")
        return redirect(url_for("market.index"))

    return render_template("add_new_source.html")


@market_bp.route("/market/dividends")
def get_dividends():
    """Get dividends for assets."""

    a = assets.get_all_assets()

    if not a:
        flash("Must add asset first.")
        return redirect(url_for("assets.add"))

    return render_template("get_dividends.html", assets=a)


@market_bp.route("/market/prices")
def get_prices():
    """Get prices for assets."""

    a = assets.get_all_assets()

    if not a:
        flash("Must add asset first.")
        return redirect(url_for("assets.add"))

    return render_template("get_prices.html", assets=a)


@market_bp.route("/market/splits")
def get_splits():
    """Get splits for assets."""

    a = assets.get_all_assets()

    if not a:
        flash("Must add asset first.")
        return redirect(url_for("assets.add"))

    return render_template("get_splits.html", assets=a)


@market_bp.route("/market/dividends/add/<int:asset_id>", methods=["POST"])
def add_dividends(asset_id):

    if market.insert_dividends_for_asset(asset_id):
        flash("Dividends added.")

    else:
        flash("Failed to load dividends.")

    return redirect(url_for("market.get_dividends"))


@market_bp.route("/market/prices/add/<int:asset_id>", methods=["POST"])
def add_prices(asset_id):
    """Insert prices for asset."""

    if market.insert_prices_for_asset(asset_id):
        flash("Prices added.")
    else:
        flash("Failed to add prices.")

    return redirect(url_for("market.get_prices"))


@market_bp.route("/market/splits/add/<int:asset_id>", methods=["POST"])
def add_splits(asset_id):
    """Insert splits for asset."""

    if market.insert_splits_for_asset(asset_id):
        flash("Splits added.")
    else:
        flash("Failed to add splits.")

    return redirect(url_for("market.get_splits"))


@market_bp.route("/market/dividends/delete/<int:asset_id>", methods=["POST"])
def delete_dividends(asset_id):
    """Delete dividends for asset."""

    if market.delete_dividends_for_asset(asset_id):
        flash("Dividends deleted.")
    else:
        flash("Failed to delete dividends.")

    return redirect(url_for("market.get_dividends"))


@market_bp.route("/market/prices/delete/<int:asset_id>", methods=["POST"])
def delete_prices(asset_id):
    """Deletes prices from asset."""

    if market.delete_prices_for_asset(asset_id):
        flash("Prices deleted.")
    else:
        flash("Failed to delete prices.")

    return redirect(url_for("market.get_prices"))


@market_bp.route("/market/splits/<int:asset_id>", methods=["POST"])
def delete_splits(asset_id):
    """Deletes stock splits from asset."""

    if market.delete_splits_for_asset(asset_id):
        flash("Splits deleted.")
    else:
        flash("No splits to delete.")

    return redirect(url_for("market.get_splits"))


@market_bp.route("/market/dividends/<int:asset_id>")
def show_dividends(asset_id):
    """Show dividends for asset."""

    dividends = market.get_dividends_for_asset(asset_id)

    if dividends:
        return render_template("show_dividends.html", dividends=dividends)

    flash("No dividends to show.")
    return redirect(url_for("market.get_dividends"))


@market_bp.route("/market/prices/<int:asset_id>")
def show_prices(asset_id):
    """Show prices for asset."""

    prices = market.get_prices_for_asset(asset_id)

    if prices:
        return render_template("show_prices.html", prices=prices)

    flash("No prices to show.")
    return redirect(url_for("market.get_prices"))


@market_bp.route("/market/splits/<int:asset_id>")
def show_splits(asset_id):
    """Show stock splits for asset."""

    splits = market.get_splits_for_asset(asset_id)

    if splits:
        return render_template("show_splits.html", splits=splits)

    flash("No splits to show.")
    return redirect(url_for("market.get_splits"))
