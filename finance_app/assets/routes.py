from flask import Blueprint, flash, request, redirect, render_template, url_for

from finance_app.accounts import accounts
from finance_app.assets import assets
from finance_app.market import market_dividends, market_prices, market_sources, market_stock_splits
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

    s = market_sources.get_all_sources()

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

    asset = assets.get_asset_by_id(asset_id)

    s = market_sources.get_all_sources()

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

    if market_prices.get_prices(asset_id):
        flash("Must delete prices first.")
        return redirect(url_for("assets.index"))

    if market_dividends.get_dividends(asset_id):
        flash("Must delete dividends first.")
        return redirect(url_for("assets.index"))

    if market_stock_splits.get_stock_splits(asset_id):
        flash("Must delete splits first.")
        return redirect(url_for("assets.index"))

    assets.delete_asset(asset_id)
    flash("Asset deleted.")

    return redirect(
        url_for("assets.show_assets", account_id=account_id, asset_id=asset_id)
    )


@assets_bp.route("/accounts/<int:account_id>/assets/<int:asset_id>/dividends")
def show_dividends_received(account_id, asset_id):
    """Show dividends received for asset."""

    dividends = assets.get_dividends_received(asset_id)

    if not dividends:
        flash("No dividends to show.")
        return redirect(url_for("analysis.get_dividends"))

    return render_template("show_dividends_received.html", dividends=dividends)


@assets_bp.route("/accounts/<int:account_id>/assets/<int:asset_id>/adjusted_transactions")
def show_adjusted_transactions(account_id, asset_id):
    """Show adjusted prices and shares for asset."""

    t = transactions.get_adjusted_transactions(asset_id)

    return render_template("show_adjusted_transactions.html", transactions=t)
