from flask import Blueprint, flash, redirect, request, render_template, url_for

from finance_app.assets import assets as assets
from finance_app.market import (
    market_dividends,
    market_prices,
    market_sources,
    market_stock_splits,
)

market_bp = Blueprint("market", __name__, template_folder="templates")


@market_bp.route("/market")
def show_market_sources():
    """Get market sources and display them in a table."""

    s = market_sources.get_all_sources()

    return render_template("show_market_sources.html", market_sources=s)


@market_bp.route("/market/<int:source_id>/assets")
def show_market_assets(source_id):
    """Show assets from market source."""

    a = assets.get_assets_from_market_source(source_id)

    return render_template("show_market_assets.html", assets=a)


@market_bp.route("/market/add", methods=["GET", "POST"])
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

        if market_sources.insert_source(display_name, source_key, p, d, s):
            flash("Source added.")
            return redirect(url_for("market.show_market_sources"))

        flash("Failed to add source.")

    return render_template("add_market_source.html")


@market_bp.route("/market/<int:source_id>/delete", methods=["POST"])
def delete_market_source(source_id):
    """Deletes source from database."""

    a = assets.get_assets_from_market_source(source_id)

    if a:
        flash("Must delete assets first.")
        return redirect(url_for("market.show_sources"))

    if market_sources.delete_source(source_id):
        flash("Source deleted.")
    else:
        flash("Failed to delete source.")

    return redirect(url_for("market.show_sources"))


@market_bp.route("/market/<int:source_id>/edit", methods=["GET", "POST"])
def update_market_source(source_id):
    """Edits source."""

    s = market_sources.get_source_by_id(source_id)

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

        if market_sources.update_source(source_id, display_name, source_key, p, d, s):
            flash("Source updated.")
        else:
            flash("Failed to update source.")

        return redirect(url_for("market.show_sources"))

    return render_template("update_source.html", source=s)


@market_bp.route("/market/<int:source_id>/assets/<int:asset_id>/prices")
def show_market_prices(source_id, asset_id):
    """Show prices for asset."""

    p = market_prices.get_prices(asset_id)

    if p:
        return render_template("show_market_prices.html", prices=p)

    flash("No prices to show.")
    return redirect(url_for("market.show_market_assets", source_id=source_id))


@market_bp.route(
    "/market/<int:source_id>/assets/<int:asset_id>/prices/add",
    methods=["POST"],
)
def add_market_prices(source_id, asset_id):
    """Insert prices for asset."""

    if market_prices.insert_prices_for_asset(asset_id):
        flash("Prices added.")
    else:
        flash("Failed to add prices.")

    return redirect(url_for("market.show_market_assets", source_id=source_id))


@market_bp.route(
    "/market/<int:source_id>/assets/<int:asset_id>/prices/delete",
    methods=["POST"],
)
def delete_market_prices(source_id, asset_id):
    """Deletes prices from asset."""

    if market_prices.delete_prices_for_asset(asset_id):
        flash("Prices deleted.")
    else:
        flash("Failed to delete prices.")

    return redirect(url_for("market.show_market_assets", source_id=source_id))


@market_bp.route("/market/<int:source_id>/assets/<int:asset_id>/dividends")
def show_market_dividends(source_id, asset_id):
    """Show dividends for asset."""

    divs = market_dividends.get_dividends(asset_id)

    if divs:
        return render_template("show_market_dividends.html", dividends=divs)

    flash("No dividends to show.")
    return redirect(url_for("market.show_market_assets", source_id=source_id))


@market_bp.route(
    "/market/<int:source_id>/assets/<int:asset_id>/dividends/add",
    methods=["POST"],
)
def add_market_dividends(source_id, asset_id):

    if market_dividends.insert_dividends_for_asset(asset_id):
        flash("Dividends added.")

    else:
        flash("Failed to load dividends.")

    return redirect(url_for("market.show_market_assets", source_id=source_id))


@market_bp.route(
    "/market/<int:source_id>/assets/<int:asset_id>/dividends/delete",
    methods=["POST"],
)
def delete_market_dividends(source_id, asset_id):
    """Delete dividends for asset."""

    if market_dividends.delete_dividends(asset_id):
        flash("Dividends deleted.")
    else:
        flash("Failed to delete dividends.")

    return redirect(url_for("market.show_market_assets", source_id=source_id))


@market_bp.route("/market/<int:source_id>/assets/<int:asset_id>/stock_splits")
def show_market_stock_splits(source_id, asset_id):
    """Show stock splits for asset."""

    s = market_stock_splits.get_stock_splits(asset_id)

    if s:
        return render_template("show_market_stock_splits.html", splits=s)

    flash("No splits to show.")
    return redirect(url_for("market.show_market_assets", source_id=source_id))


@market_bp.route(
    "/market/<int:source_id>/assets/<int:asset_id>/stock_splits/add",
    methods=["POST"],
)
def add_market_stock_splits(source_id, asset_id):
    """Insert splits for asset."""

    if market_stock_splits.insert_stock_splits(asset_id):
        flash("Splits added.")
    else:
        flash("Failed to add splits.")

    return redirect(url_for("market.show_market_assets", source_id=source_id))


@market_bp.route(
    "/market/<int:source_id>/assets/<int:asset_id>/stock_splits/delete",
    methods=["POST"],
)
def delete_market_stock_splits(source_id, asset_id):
    """Deletes stock splits from asset."""

    if market_stock_splits.delete_stock_splits(asset_id):
        flash("Splits deleted.")
    else:
        flash("No splits to delete.")

    return redirect(url_for("market.show_market_assets", source_id=source_id))
