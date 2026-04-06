import sqlite3
import datetime as dt

from flask import current_app, g


def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()


def convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return dt.date.fromisoformat(val.decode())


sqlite3.register_converter("date", convert_date)
sqlite3.register_adapter(dt.date, adapt_date_iso)


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = dict_factory

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db(app):
    """Use this function to initialise database from Python shell"""
    
    with app.app_context():
        db = get_db()
        with app.open_resource("schema.sql", mode="r") as f:
            db.executescript(f.read())


def insert_db(query, args=()):
    db = get_db()
    db.execute(query, args)
    db.commit()
    return


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    res = cur.fetchall()
    cur.close()
    return (res[0] if res else None) if one else res


def init_app(app):
    app.teardown_appcontext(close_db)
