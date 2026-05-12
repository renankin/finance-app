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


def init_db():
    """Use this function to initialise database from Python shell."""

    with current_app.app_context():
        db = get_db()
        with current_app.open_resource("schema.sql", mode="r") as f:
            db.executescript(f.read())
        db.commit()


def execute_db(query: str, args=()):
    """Insert a command in the database. If args is a list it will insert all entries
      into database."""

    db = get_db()
    
    if isinstance(args, list):
        cur = db.executemany(query, args)
    else:
        cur = db.execute(query, args)

    cur.close()
    db.commit()



def query_db(query: str, args=(), one=False):
    """Query the database.
    * if `One` is True, returns the result from only one row
    (either single value or dictionary), otherwise returns a list."""

    cur = get_db().execute(query, args)
    res = cur.fetchall()
    cur.close()

    if res:
        n_arguments = len(res[0])
        if one:
            if n_arguments == 1:  # Returns single value
                return next(iter(res[0].values()))
            else:  # Returns dictionary
                return res[0]
        else:
            if n_arguments == 1:  # Return list of values
                return [next(iter(entry.values())) for entry in res]
            else:
                return res  # Returns list of dictonaries

    return None


def init_app(app):
    app.teardown_appcontext(close_db)
