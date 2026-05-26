from flask import Blueprint, flash, request, redirect, render_template, url_for

from finance_app.accounts import repository as accounts
from finance_app.assets import repository as assets
from finance_app.market import dividends, prices, sources, splits
from finance_app.transactions import repository as transactions

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

    if splits.get_splits_for_asset(asset_id):
        flash("Must delete splits first.")
        return redirect(url_for("assets.index"))

    assets.delete_asset(asset_id)
    flash("Asset deleted.")

    return redirect(
        url_for("assets.show_assets", account_id=account_id, asset_id=asset_id)
    )
