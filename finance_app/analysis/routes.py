from flask import Blueprint, flash, redirect, render_template, url_for

from finance_app.analysis import repository as analysis

analysis_bp = Blueprint("analysis", __name__, template_folder="templates")


@analysis_bp.route("/accounts/<int:account_id>/analysis/return")
def show_account_return(account_id):
    """Displays the return on investiment for each asset own"""

    a = analysis.get_return_for_assets(account_id)

    if not a:
        flash("No assets to show. Must add asset first.")
        return redirect(url_for("assets.add"))

    return render_template("show_return.html", assets=a)
