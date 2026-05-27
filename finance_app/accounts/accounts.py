from finance_app.db import query_db, execute_db


def delete_account(account_id):
    """Delete account."""

    execute_db("DELETE FROM accounts WHERE account_id = ?", (account_id,))


def get_all_accounts() -> list:
    """Fetches all accounts from database and returns a list of dictionaries containing
    `account_id`, `account_name` and `currency`."""

    accounts = query_db("SELECT account_id, account_name, currency FROM accounts")

    if accounts:
        return accounts

    return []


def get_account_by_id(account_id: int) -> dict:
    """Fetch account from database based on the id and returns a dictionary containing
    `account_id`, `account_name` and `currency`."""

    account = query_db(
        "SELECT account_id, account_name, currency FROM accounts WHERE account_id = ?",
        (account_id,),
        one=True,
    )

    if account:
        return account

    return {}


def insert_account(account_name: str, currency: str):
    """Insert account in database."""

    execute_db(
        "INSERT INTO accounts (account_name, currency) VALUES (?, ?)",
        (account_name, currency),
    )


def update_account(account_id: int, account_name: str, currency: str):
    """Update account."""

    execute_db(
        "UPDATE accounts SET account_name = ?, currency = ? WHERE account_id = ?",
        (account_name, currency, account_id),
    )
