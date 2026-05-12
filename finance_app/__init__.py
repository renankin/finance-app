import os
from flask import Flask

from finance_app import db, filters
from finance_app.accounts.routes import accounts_bp
from finance_app.analysis.routes import analysis_bp
from finance_app.assets.routes import assets_bp
from finance_app.market.routes import market_bp
from finance_app.transactions.routes import transactions_bp


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, 'transactions.db'),
    )

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    app.jinja_env.filters["format_currency"] = filters.format_currency
    app.jinja_env.filters["format_date"] = filters.format_date

    app.register_blueprint(accounts_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(transactions_bp)

    return app
