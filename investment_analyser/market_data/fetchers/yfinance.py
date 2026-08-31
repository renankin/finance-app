from pandas import DataFrame, Series
from yfinance import Ticker
from yfinance.exceptions import YFException


class YFetcher:
    def __init__(self, symbol: str):

        self.ticker = Ticker(symbol)

        try:
            self.info = self.ticker.info
        except YFException:
            self.ticker = None

    def is_etf(self) -> bool:

        return self.info.get("quoteType") == "ETF"

    def is_stock(self) -> bool:

        return self.info.get("quoteType") == "EQUITY"

    def get_dividends(self) -> Series:

        if self.ticker:
            if not self.is_stock():
                return Series()

            divs = self.ticker.dividends

            if divs.empty:
                return Series()

            return divs

        return Series()

    def get_prices(self) -> Series:

        if not self.ticker:
            return Series()

        history = self.ticker.history(period="max", auto_adjust=False)

        if history.empty:
            return Series()

        return history["Close"].dropna()

    def get_stock_splits(self) -> Series:

        if self.ticker:
            if not self.is_stock():
                return Series()

            splits = self.ticker.splits

            if splits.empty:
                return Series()

            return splits

        return Series()

    def get_top_holdings(self) -> DataFrame:
        """Returns a Dataframe with columns `Name` and `Holding Percent`
        which is indexed with `Symbol`. The DataFrame is sorted by holding percent."""

        if self.ticker and self.is_etf():
            return self.ticker.funds_data.top_holdings.sort_values(
                "Holding Percent", ascending=False
            )

        return DataFrame()

    def get_sector_weighting(self) -> dict:
        """Returns a dictionary contianing sector key and sector weight for the asset
        sorted by ascending order.
        """

        if self.ticker:
            if self.is_etf():
                sector_weightings = self.ticker.funds_data.sector_weightings

                sorted_list = sorted(
                    sector_weightings.items(), key=lambda item: item[1], reverse=True
                )

                return {
                    sector_key: sector_weight
                    for (sector_key, sector_weight) in sorted_list
                }

            if self.is_stock():
                sector_key = self.get_info("sectorKey")
                return {sector_key: 1}

        return {}

    def get_info(self, key: str):
        """Returns the info requested via the `key` parameter from the `Ticker` class
        from yfinance if found, `None` if not found.

        Some valid keys:

        * `symbol`
        * `currency`
        * `longName`
        * `netAssets`
        * `netExpenseRatio`
        * `sectorKey`
        """

        if not self.ticker:
            return None

        return self.info.get(key)
