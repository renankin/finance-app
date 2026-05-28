from flask import Blueprint, flash, redirect, request, render_template, url_for

from finance_app.assets import assets as assets
from finance_app.market import sources, dividends, prices, stock_splits

market_bp = Blueprint("market", __name__, template_folder="templates")


@market_bp.route("/market/sources")
def show_market_sources():
    """Get market sources and display them in a table."""

    s = sources.get_all_sources()

    return render_template("show_sources.html", market_sources=s)


@market_bp.route("/market/sources/add", methods=["GET", "POST"])
def add_market_source():
    """Add new source."""

    if request.method == "POST":
        display_name = request.form.get("source_name")
        source_key = request.form.get("source_key")
        p = request.form.get("supports_prices", type=bool)
        d = request.form.get("supports_dividends", type=bool)
        s = request.form.get("supports_splits", type=bool)

        if not p:
            p = False
        if not d:
            d = False
        if not s:
            s = False

        if sources.insert_source(display_name, source_key, p, d, s):
            flash("Source added.")
            return redirect(url_for("market.show_sources"))

        flash("Failed to add source.")

    return render_template("add_source.html")


@market_bp.route("/market/sources/<int:source_id>/delete", methods=["POST"])
def delete_market_source(source_id):
    """Deletes source from database."""

    a = assets.get_assets_from_source(source_id)

    if a:
        flash("Must delete assets first.")
        return redirect(url_for("market.show_sources"))

    if sources.delete_source(source_id):
        flash("Source deleted.")
    else:
        flash("Failed to delete source.")

    return redirect(url_for("market.show_sources"))


@market_bp.route("/market/sources/<int:source_id>/edit", methods=["GET", "POST"])
def update_market_source(source_id):
    """Edits source."""

    s = sources.get_source_by_id(source_id)

    if request.method == "POST":
        display_name = request.form.get("source_name")
        source_key = request.form.get("source_key")
        p = request.form.get("supports_prices", type=bool)
        d = request.form.get("supports_dividends", type=bool)
        s = request.form.get("supports_splits", type=bool)

        if not p:
            p = False
        if not d:
            d = False
        if not s:
            s = False

        if sources.update_source(source_id, display_name, source_key, p, d, s):
            flash("Source updated.")
        else:
            flash("Failed to update source.")

        return redirect(url_for("market.show_sources"))

    return render_template("update_source.html", source=s)


@market_bp.route("/market/accounts/<int:account_id>/assets/<int:asset_id>/prices")
def show_prices(account_id, asset_id):
    """Show prices for asset."""

    p = prices.get_prices(asset_id)

    if p:
        return render_template("show_prices.html", prices=p)

    flash("No prices to show.")
    return redirect(url_for("assets.show_assets", account_id=account_id))


@market_bp.route(
    "/market/accounts/<int:account_id>/assets/<int:asset_id>/prices/add",
    methods=["POST"],
)
def add_prices(account_id, asset_id):
    """Insert prices for asset."""

    if prices.insert_prices_for_asset(asset_id):
        flash("Prices added.")
    else:
        flash("Failed to add prices.")

    return redirect(url_for("assets.show_assets", account_id=account_id))


@market_bp.route(
    "/market/accounts/<int:account_id>/assets/<int:asset_id>/prices/delete",
    methods=["POST"],
)
def delete_prices(account_id, asset_id):
    """Deletes prices from asset."""

    if prices.delete_prices_for_asset(asset_id):
        flash("Prices deleted.")
    else:
        flash("Failed to delete prices.")

    return redirect(url_for("assets.show_assets", account_id=account_id))


@market_bp.route("/market/accounts/<int:account_id>/assets/<int:asset_id>/dividends")
def show_dividends(account_id, asset_id):
    """Show dividends for asset."""

    divs = dividends.get_dividends(asset_id)

    if divs:
        return render_template("show_dividends.html", dividends=divs)

    flash("No dividends to show.")
    return redirect(url_for("assets.show_assets", account_id=account_id))


@market_bp.route(
    "/market/accounts/<int:account_id>/assets/<int:asset_id>/dividends/add",
    methods=["POST"],
)
def add_dividends(account_id, asset_id):

    if dividends.insert_dividends_for_asset(asset_id):
        flash("Dividends added.")

    else:
        flash("Failed to load dividends.")

    return redirect(url_for("assets.show_assets", account_id=account_id))


@market_bp.route(
    "/market/accounts/<int:account_id>/assets/<int:asset_id>/dividends/delete",
    methods=["POST"],
)
def delete_dividends(account_id, asset_id):
    """Delete dividends for asset."""

    if dividends.delete_dividends(asset_id):
        flash("Dividends deleted.")
    else:
        flash("Failed to delete dividends.")

    return redirect(url_for("assets.show_assets", account_id=account_id))


@market_bp.route("/market/accounts/<int:account_id>/assets/<int:asset_id>/stock_splits")
def show_stock_splits(account_id, asset_id):
    """Show stock splits for asset."""

    s = stock_splits.get_stock_splits(asset_id)

    if s:
        return render_template("show_stock_splits.html", splits=s)

    flash("No splits to show.")
    return redirect(url_for("assets.show_assets", account_id=account_id))


@market_bp.route(
    "/market/accounts/<int:account_id>/assets/<int:asset_id>/stock_splits/add",
    methods=["POST"],
)
def add_stock_splits(account_id, asset_id):
    """Insert splits for asset."""

    if stock_splits.insert_stock_splits(asset_id):
        flash("Splits added.")
    else:
        flash("Failed to add splits.")

    return redirect(url_for("assets.show_assets", account_id=account_id))


@market_bp.route(
    "/market/accounts/<int:account_id>/assets/<int:asset_id>/stock_splits/delete",
    methods=["POST"],
)
def delete_stock_splits(account_id, asset_id):
    """Deletes stock splits from asset."""

    if stock_splits.delete_stock_splits(asset_id):
        flash("Splits deleted.")
    else:
        flash("No splits to delete.")

    return redirect(url_for("assets.show_assets", account_id=account_id))
