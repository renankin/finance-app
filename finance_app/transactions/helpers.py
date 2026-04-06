import datetime as dt
from flask import flash


def get_form_params(**data):

    if "symbol" in data:
        if not data["symbol"]:
            flash("Must provide symbol.")
            return None

        data["symbol"] = data["symbol"].upper()

    if "date" in data:
        try:
            data["date"] = dt.date.fromisoformat(data["date"])
        except ValueError:
            flash("Invalid date format.")
            return None

        if data["date"] > dt.datetime.now().date():
            flash("Cannot provide future date.")
            return None

    if "shares" in data:
        try:
            data["shares"] = float(data["shares"])
        except ValueError:
            flash("Shares is not numeric or not exist.")
            return None

    if "price" in data:
        try:
            data["price"] = float(data["price"])
        except ValueError:
            flash("Must provide valid price.")
            return None

    return data
