from flask import Blueprint, flash, request, redirect, render_template, url_for

from finance_app.accounts import repository as accounts
from finance_app.assets import repository as assets
from finance_app.market import repository as market
from finance_app.transactions import repository as transactions

assets_bp = Blueprint("assets", __name__, template_folder="templates")


@assets_bp.route("/assets")
def index():
    """Show list of assets currently in account."""

    if not accounts.get_all_accounts():
        return redirect(url_for("accounts.index"))

    a = assets.get_all_assets()

    if a:
        return render_template("assets.html", assets=a)

    flash("No assets to show. Must add asset first.")
    return redirect(url_for("assets.add"))


@assets_bp.route("/assets/add", methods=["POST", "GET"])
def add():
    """Add new asset for account."""

    a = accounts.get_all_accounts()

    if not a:
        flash("No accounts. Must add account first.")
        return redirect(url_for("accounts.add"))

    if request.method == "POST":
        account_id = request.form.get("account_id", type=int)
        asset_name = request.form.get("asset_name")
        asset_type = request.form.get("asset_type")
        still_open = request.form.get("still_open", type=int)

        assets.insert_asset(account_id, asset_name, asset_type, still_open)
        flash("Asset added.")
        return redirect(url_for("assets.index"))

    return render_template("add_asset.html", accounts=a)


@assets_bp.route("/assets/edit/<int:asset_id>", methods=["POST", "GET"])
def edit(asset_id):
    """Edit asset."""

    if request.method == "POST":
        account_id = request.form.get("account_id", type=int)
        asset_name = request.form.get("asset_name")
        asset_type = request.form.get("asset_type")
        still_open = request.form.get("still_open", type=int)

        assets.update_asset(asset_id, account_id, asset_name, asset_type, still_open)
        flash("Asset updated.")
        return redirect(url_for("assets.index"))

    return render_template("edit_asset.html", asset=assets.get_asset_by_id(asset_id))


@assets_bp.route("/assets/delete/<int:asset_id>", methods=["POST"])
def delete(asset_id):
    """Delete asset."""

    if transactions.get_transactions_from_asset(asset_id):
        flash("Must delete transactions first.")
        return redirect(url_for("assets.index"))
    
    if market.get_prices_for_asset(asset_id):
        flash("Must delete prices first.")
        return redirect(url_for("assets.index"))

    if market.get_dividends_for_asset(asset_id):
        flash("Must delete dividends first.")
        return redirect(url_for("assets.index"))
    
    if market.get_splits_for_asset(asset_id):
        flash("Must delete splits first.")
        return redirect(url_for("assets.index"))
    
    assets.delete_asset(asset_id)
    flash("Asset deleted.")

    return redirect(url_for("assets.index"))
