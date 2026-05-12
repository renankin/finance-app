import yfinance as yf


def get_prices(symbol: str) -> dict:
    """Get prices from yfinance"""

    history = yf.Ticker(symbol).history(period="max", auto_adjust=False)

    if history.empty:
        return {}

    prices = []

    for index, row in history.iterrows():
        prices.append({"date": index.date(), "price": float(row["Close"])})

    return prices


def get_dividends(symbol: str) -> dict:
    """Get dividends from yfinance"""

    divs = yf.Ticker(symbol).dividends

    if divs.empty:
        return {}

    vals = []

    for index, div in divs.items():
        vals.append({"date": index.date(), "dividend": float(div)})

    return vals


def get_splits(symbol: str) -> dict:
    """Get stock splits from yfinance"""

    splits = yf.Ticker(symbol).splits

    if splits.empty:
        return {}

    vals = []

    for index, split_ratio in splits.items():
        vals.append({"date": index.date(), "split_ratio": float(split_ratio)})

    return vals
