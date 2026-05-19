from finance_app.market.fetchers import yfinance_fetcher, tesouro_fetcher

# Map market source key with module name
FETCHER_REGISTRY = {
    "yfinance": yfinance_fetcher,
    "tesouro_website": tesouro_fetcher,
}


class FetcherProtocol:
    def __init__(self, market_source: dict):
        """Constructor for a class to fetch market information. Needs to provide
        `market_source` with keys `source_key`, `supports_dividends`, `supports_prices`
         and `supports_stock_splits` to correlate with market APIs saved."""

        self.module = FETCHER_REGISTRY[market_source["source_key"]]

        self.supports_dividends = market_source["supports_dividends"]
        self.supports_prices = market_source["supports_prices"]
        self.supports_splits = market_source["supports_stock_splits"]

    def fetch_dividends(self, symbol: str) -> list[dict]:
        """Fetches dividends from source and returns a list of dictionaries containing
        `date` and `dividend` keys."""

        if self.supports_dividends:
            return self.module.get_dividends(symbol)
        
        return []

    def fetch_prices(self, symbol: str) -> list[dict]:
        """Fetches daily prices from source and returns a list of dictionaries
        containing `date` and `price` keys."""

        if self.supports_prices:        
            return self.module.get_prices(symbol)
        
        return []

    def fetch_stock_splits(self, symbol: str) -> list[dict]:
        """Fetches stock splits from source and returns a list of dictionaries
        containing `date` and `split_ratio` keys."""

        if self.supports_splits:
            return self.module.get_stock_splits(symbol)
        
        return []
