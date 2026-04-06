import os
from flask import Flask

from finance_app import db, filters
from finance_app.stocks import stocks
from finance_app.transactions import transactions
from finance_app.roi import roi


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, 'transactions.db'),
    )

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    db.init_db(app)

    app.jinja_env.filters["format_currency"] = filters.format_currency
    app.jinja_env.filters["format_date"] = filters.format_date

    app.register_blueprint(stocks.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(roi.bp)

    return app
