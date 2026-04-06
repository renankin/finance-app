import datetime as dt

def format_currency(value, currency):
    """Takes currency input and returns formatted price value"""

    map = {
        "USD": "$",
        "BRL": "R$",
    }

    if currency in map:
        return f"{map[currency]} {value:,.2f}"
    else:
        return None


def format_date(date):
    """Takes format and format string"""

    return dt.date.strftime(date, "%d/%m/%Y")