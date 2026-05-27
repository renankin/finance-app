from flask import Blueprint, flash, request, redirect, render_template, url_for

from finance_app.accounts import accounts
from finance_app.assets import assets, dividends, prices, stock_splits
from finance_app.market import sources
from finance_app.transactions import transactions

assets_bp = Blueprint("assets", __name__, template_folder="templates")


@assets_bp.route("/accounts/<int:account_id>/assets")
def show_assets(account_id):
    """Show list of assets in account."""

    ass = assets.get_assets_from_account(account_id)

    acc = accounts.get_account_by_id(account_id)

    if ass:
        return render_template("show_assets.html", assets=ass, account=acc)

    flash("No assets to show. Must add asset first.")
    return redirect(url_for("assets.add_asset", account_id=account_id))


@assets_bp.route("/accounts/<int:account_id>/assets/add", methods=["POST", "GET"])
def add_asset(account_id):
    """Add new asset for account."""

    s = sources.get_all_sources()

    acc = accounts.get_account_by_id(account_id)

    if request.method == "POST":
        asset_name = request.form.get("asset_name")
        market_source_id = request.form.get("market_source_id", type=int)
        still_open = request.form.get("still_open", type=bool)

        if not still_open:
            still_open = False

        assets.insert_asset(account_id, asset_name, market_source_id, still_open)
        flash("Asset added.")
        return redirect(url_for("assets.show_assets", account_id=account_id))

    return render_template("add_asset.html", sources=s, account=acc)


@assets_bp.route(
    "/accounts/<int:account_id>/assets/<int:asset_id>/edit", methods=["POST", "GET"]
)
def edit_asset(account_id, asset_id):
    """Edit asset."""

    account = accounts.get_account_by_id(account_id)

    asset = assets.get_asset_by_id(account_id, asset_id)

    s = sources.get_all_sources()

    if request.method == "POST":
        asset_name = request.form.get("asset_name")
        market_source_id = request.form.get("market_source_id", type=int)
        still_open = request.form.get("still_open", type=bool)

        if not still_open:
            still_open = False

        assets.update_asset(
            asset_id, account_id, asset_name, market_source_id, still_open
        )
        flash("Asset updated.")
        return redirect(url_for("assets.show_assets", account_id=account_id))

    return render_template(
        "edit_asset.html", account=account, asset=asset, market_sources=s
    )


@assets_bp.route(
    "/accounts/<int:account_id>/assets/delete/<int:asset_id>", methods=["POST"]
)
def delete_asset(account_id, asset_id):
    """Delete asset."""

    if transactions.get_transactions_from_asset(account_id, asset_id):
        flash("Must delete transactions first.")
        return redirect(url_for("assets.index"))

    if prices.get_prices_for_asset(asset_id):
        flash("Must delete prices first.")
        return redirect(url_for("assets.index"))

    if dividends.get_dividends_for_asset(asset_id):
        flash("Must delete dividends first.")
        return redirect(url_for("assets.index"))

    if splits.get_stock_splits(asset_id):
        flash("Must delete splits first.")
        return redirect(url_for("assets.index"))

    assets.delete_asset(asset_id)
    flash("Asset deleted.")

    return redirect(
        url_for("assets.show_assets", account_id=account_id, asset_id=asset_id)
    )


@assets_bp.route("/accounts/<int:account_id>/assets/<int:asset_id>/prices")
def show_prices(account_id, asset_id):
    """Show prices for asset."""

    p = prices.get_prices_for_asset(asset_id)

    if p:
        return render_template("show_prices.html", prices=p)

    flash("No prices to show.")
    return redirect(url_for("assets.show_assets", account_id=account_id))


@assets_bp.route(
    "/accounts/<int:account_id>/assets/<int:asset_id>/prices/add", methods=["POST"]
)
def add_prices(account_id, asset_id):
    """Insert prices for asset."""

    if prices.insert_prices_for_asset(asset_id):
        flash("Prices added.")
    else:
        flash("Failed to add prices.")

    return redirect(url_for("assets.show_assets", account_id=account_id))


@assets_bp.route(
    "/accounts/<int:account_id>/assets/<int:asset_id>/prices/delete", methods=["POST"]
)
def delete_prices(account_id, asset_id):
    """Deletes prices from asset."""

    if prices.delete_prices_for_asset(asset_id):
        flash("Prices deleted.")
    else:
        flash("Failed to delete prices.")

    return redirect(url_for("assets.show_assets", account_id=account_id))


@assets_bp.route("/accounts/<int:account_id>/assets/<int:asset_id>/dividends")
def show_dividends(account_id, asset_id):
    """Show dividends for asset."""

    divs = dividends.get_dividends_for_asset(asset_id)

    if divs:
        return render_template("show_dividends.html", dividends=divs)

    flash("No dividends to show.")
    return redirect(url_for("assets.show_assets", account_id=account_id))


@assets_bp.route(
    "/accounts/<int:account_id>/assets/<int:asset_id>/dividends/add", methods=["POST"]
)
def add_dividends(account_id, asset_id):

    if dividends.insert_dividends_for_asset(asset_id):
        flash("Dividends added.")

    else:
        flash("Failed to load dividends.")

    return redirect(url_for("assets.show_assets", account_id=account_id))


@assets_bp.route(
    "/accounts/<int:account_id>/assets/<int:asset_id>/dividends/delete",
    methods=["POST"],
)
def delete_dividends(account_id, asset_id):
    """Delete dividends for asset."""

    if dividends.delete_dividends_for_asset(asset_id):
        flash("Dividends deleted.")
    else:
        flash("Failed to delete dividends.")

    return redirect(url_for("assets.show_assets", account_id=account_id))


@assets_bp.route("/accounts/<int:account_id>/assets/<int:asset_id>/stock_splits")
def show_stock_splits(account_id, asset_id):
    """Show stock splits for asset."""

    s = stock_splits.get_stock_splits(asset_id)

    if s:
        return render_template("show_stock_splits.html", splits=s)

    flash("No splits to show.")
    return redirect(url_for("assets.show_assets", account_id=account_id))


@assets_bp.route(
    "/accounts/<int:account_id>/assets/<int:asset_id>/stock_splits/add",
    methods=["POST"],
)
def add_stock_splits(account_id, asset_id):
    """Insert splits for asset."""

    if stock_splits.insert_stock_splits(asset_id):
        flash("Splits added.")
    else:
        flash("Failed to add splits.")

    return redirect(url_for("assets.show_assets", account_id=account_id))


@assets_bp.route(
    "/accounts/<int:account_id>/assets/<int:asset_id>/stock_splits/delete",
    methods=["POST"],
)
def delete_stock_splits(account_id, asset_id):
    """Deletes stock splits from asset."""

    if stock_splits.delete_stock_splits(asset_id):
        flash("Splits deleted.")
    else:
        flash("No splits to delete.")

    return redirect(url_for("assets.show_assets", account_id=account_id))
