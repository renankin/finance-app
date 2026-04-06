import yfinance as yf

from finance_app.db import query_db

MIN_SHARES = 10


def lookup_stock(symbol):
    """Checks the price and stock symbol"""

    ticker = yf.Ticker(symbol)

    if ticker.history().empty:
        return None

    quote = {
        "name": ticker.info["longName"],
        "currency": ticker.info["currency"],
        "currentPrice": ticker.info["currentPrice"],
        "previousClose": ticker.info["previousClose"],
    }

    if not ticker.splits.empty:
        quote["splits"] = []
        for split, ratio in ticker.splits.items():
            quote["splits"].append({"date": split.date(), "ratio": ratio})
    else:
        quote["splits"] = None

    return quote


def get_dividends(symbol):
    """Get dividends from yfinance"""

    rates = yf.Ticker(symbol).dividends

    if rates.empty:
        return None

    transactions = get_transactions(symbol)
    dividends = {"values": [], "dates": []}

    for div, div_rate in rates.items():
        div_shares = sum(
            t["adj_shares"] for t in transactions if t["date"] <= div.date()
        )

        if div_shares > MIN_SHARES:
            dividends["values"].append(div_rate * div_shares)
            dividends["dates"].append(div.date())

    return dividends


def get_hist_prices(symbol, date):
    """Get hystorical prices for stock"""

    ticker = yf.Ticker(symbol)
    history = ticker.history(period="max", auto_adjust=False)

    if history.empty:
        return None

    # Get the most recent price valid
    df = history[history.index <= date.isoformat()]

    if df.empty:
        return None

    price = df.iloc[-1]

    return {
        "currency": ticker.info["currency"],
        "date": price.name.date(),
        "close": price["Close"],
        "high": price["High"],
        "low": price["Low"],
    }


def get_transactions(symbol):
    """Fetches transactions from database and adjust stock splits"""

    transactions = query_db("SELECT * FROM transactions WHERE symbol = ?", [symbol])

    if not transactions:
        return None

    for t in transactions:
        t["adj_shares"] = t["shares"]
        t["adj_price"] = t["price"]

        info = lookup_stock(symbol)

        if info["splits"]:
            for split in info["splits"]:
                if t["date"] <= split["date"]:
                    t["adj_shares"] *= split["ratio"]
                    t["adj_price"] /= split["ratio"]

    return transactions
