import yfinance as yf


def get_prices(symbol: str) -> list[dict]:
    """Get prices from yfinance and returns a list of dictionaries containing
    `date` and `price` keys"""

    history = yf.Ticker(symbol).history(period="max", auto_adjust=False)

    if history.empty:
        return {}

    prices = []

    for index, row in history.iterrows():
        if not row.isna().any():
            prices.append({"date": index.date(), "price": float(row["Close"])})

    return prices


def get_dividends(symbol: str) -> list[dict]:
    """Get dividends from yfinance and returns a list of dictionaries containing
    `date` and `dividend` keys"""

    divs = yf.Ticker(symbol).dividends

    if divs.empty:
        return {}

    vals = []

    for index, div in divs.items():
        vals.append({"date": index.date(), "dividend": float(div)})

    return vals


def get_stock_splits(symbol: str) -> list[dict]:
    """Get stock splits from yfinance and returns a list of dictionaries containing
    `date` and `split_ratio` keys"""

    splits = yf.Ticker(symbol).splits

    if splits.empty:
        return {}

    vals = []

    for index, split_ratio in splits.items():
        vals.append({"date": index.date(), "split_ratio": float(split_ratio)})

    return vals
