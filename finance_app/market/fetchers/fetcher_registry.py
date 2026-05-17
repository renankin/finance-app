from finance_app.market.fetchers import yfinance_fetcher, tesouro_fetcher


FETCHER_REGISTRY = {
    "yfinance": yfinance_fetcher,
    "tesouro_website": tesouro_fetcher,
}


class FetcherProtocol:
    def __init__(self, fetcher_key: str):
        """Constructor for a class to fetch market information. Needs to provide
        `fetcher_key` to correlate with market APIs saved."""

        self.module = FETCHER_REGISTRY[fetcher_key]

    def fetch_dividends(self, symbol: str) -> list[dict]:
        """Fetches dividends from source and returns a list of dictionaries containing
        `date` and `dividend` keys."""

        return self.module.get_dividends(symbol)

    def fetch_prices(self, symbol: str) -> list[dict]:
        """Fetches daily prices from source and returns a list of dictionaries
        containing `date` and `price` keys."""

        return self.module.get_prices(symbol)

    def fetch_stock_splits(self, symbol: str) -> list[dict]:
        """Fetches stock splits from source and returns a list of dictionaries
        containing `date` and `split_ratio` keys."""

        return self.module.get_stock_splits(symbol)
