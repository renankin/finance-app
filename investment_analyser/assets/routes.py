from flask import Blueprint, flash, redirect, render_template, request, url_for

from investment_analyser.accounts import accounts
from investment_analyser.assets import assets
from investment_analyser.market_data.repository import dividends, prices, stock_splits
from investment_analyser.transactions import transactions

assets_bp = Blueprint("assets", __name__, template_folder="templates")


@assets_bp.route("/assets")
def index():
    """Show list of assets in account."""

    asset_search = request.args.get("search")
    if not asset_search:
        asset_search = ""

    all_assets = []
    for asset in assets.get_all_assets():
        if asset_search.upper() in asset["asset_symbol"].upper():
            all_assets.append(asset)

    return render_template("show_assets.html", assets=all_assets)


@assets_bp.route("/assets/add", methods=["POST", "GET"])
def add():
    """Add new asset for account."""

    all_accounts = accounts.get_all_accounts()

    if not all_accounts:
        flash("No accounts. Must add account first.")
        return redirect(url_for("accounts.add"))

    if request.method == "POST":
        account_id = request.form.get("account_id", type=int)
        asset_symbol = request.form.get("asset_symbol")
        asset_name = request.form.get("asset_name")
        benchmark_index = request.form.get("benchmark_index")
        expense_ratio = request.form.get("expense_ratio", type=float)
        total_assets = request.form.get("total_assets", type=float)
        asset_type = request.form.get("asset_type")
        still_open = request.form.get("still_open", type=bool)

        if not still_open:
            still_open = False

        assets.insert_asset(
            account_id,
            asset_symbol,
            asset_name,
            benchmark_index,
            expense_ratio,
            total_assets,
            asset_type,
            still_open,
        )
        flash("Asset added.")
        return redirect(url_for("assets.index"))

    return render_template("add_asset.html", accounts=all_accounts)


@assets_bp.route("/assets/<int:asset_id>/edit", methods=["POST", "GET"])
def edit(asset_id):
    """Edit asset."""

    asset = assets.get_asset(asset_id)

    if request.method == "POST":
        asset_symbol = request.form.get("asset_symbol")
        asset_name = request.form.get("asset_name")
        benchmark_index = request.form.get("benchmark_index")
        expense_ratio = request.form.get("expense_ratio", type=float)
        total_assets = request.form.get("total_assets", type=float)
        asset_type = request.form.get("asset_type")
        still_open = request.form.get("still_open", type=bool)

        if not still_open:
            still_open = False

        assets.edit_asset(
            asset_id,
            asset_symbol,
            asset_name,
            benchmark_index,
            expense_ratio,
            total_assets,
            asset_type,
            still_open,
        )
        flash("Asset updated.")
        return redirect(url_for("assets.index"))

    return render_template("edit_asset.html", asset=asset, asset_id=asset_id)


@assets_bp.route("/assets/<int:asset_id>/delete", methods=["POST"])
def delete(asset_id):
    """Delete asset."""

    if transactions.get_transactions(asset_id):
        flash("Must delete transactions first.")
        return redirect(url_for("assets.index"))

    if prices.get_prices(asset_id):
        flash("Must delete prices first.")
        return redirect(url_for("assets.index"))

    if dividends.get_dividends(asset_id):
        flash("Must delete dividends first.")
        return redirect(url_for("assets.index"))

    if stock_splits.get_stock_splits(asset_id):
        flash("Must delete splits first.")
        return redirect(url_for("assets.index"))

    assets.delete_asset(asset_id)
    flash("Asset deleted.")

    return redirect(url_for("assets.index"))


@assets_bp.route("/assets/<int:asset_id>/dividends")
def show_dividends(asset_id):
    """Show dividends received for asset."""

    dividends = assets.get_dividends_received(asset_id)

    asset = assets.get_asset(asset_id)

    account = accounts.get_account(asset["account_id"])

    if not dividends:
        flash("No dividends to show.")
        return redirect(url_for("assets.index"))

    return render_template(
        "show_dividends_received.html",
        dividends=dividends,
        currency=account["currency"],
        asset_id=asset_id,
    )
