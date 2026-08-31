from pandas import Series

from investment_analyser.assets import assets
from investment_analyser.filters import format_currency, format_percent
from investment_analyser.market_analysis.price_analyser import calculate_price_change
from investment_analyser.market_data.fetchers.yfinance import YFetcher
from investment_analyser.market_data.repository import prices


def format_etf_table(symbol: str) -> dict:
    """Include something here."""

    fetcher = YFetcher(symbol)
    watchlist = assets.get_asset(asset_symbol=symbol)
    if not fetcher.is_etf():
        underlying_symbol = assets.get_etf_data(watchlist["asset_id"])["underlying_etf_symbol"]
        fetcher = YFetcher(underlying_symbol)

    basic_info = {}
    if watchlist:
        basic_info["Symbol"] = watchlist["asset_symbol"]
        basic_info["Name"] = watchlist["asset_name"]
        basic_info["Benchmark index"] = watchlist["benchmark_index"]
        basic_info["Net expense ratio"] = format_percent(
            watchlist["expense_ratio"], in_percent=True
        )
        basic_info["Total assets"] = format_currency(
            watchlist["total_assets"], fetcher.get_info("currency")
        )
    else:
        basic_info["Symbol"] = fetcher.get_info("symbol")
        basic_info["Name"] = fetcher.get_info("longName")
        basic_info["Net expense ratio"] = format_percent(
            fetcher.get_info("netExpenseRatio"), in_percent=True
        )
        basic_info["Total assets"] = format_currency(
            fetcher.get_info("netAssets"), fetcher.get_info("currency")
        )

    performance = {}
    years = [1, 3, 5, 10]
    for year in years:
        if watchlist:
            asset_prices = prices.get_prices(watchlist["asset_id"])
            prices_ser = Series(
                data=[item["unit_price"] for item in asset_prices],
                index=[item["date"] for item in asset_prices],
            )
            price_change = calculate_price_change(prices_ser, year)
        else:
            price_change = calculate_price_change(fetcher.get_prices(), year)

        performance[f"{year}-year change"] = format_percent(price_change)

    sector_weighting = {}
    i = 1
    for (sector_key, sector_weight) in fetcher.get_sector_weighting().items():
        sector_weighting[f"sector_{i}"] = (
            f"{sector_key} ({format_percent(sector_weight)})"
        )
        i += 1


    top_holdings = {}
    i = 1
    for _, row in fetcher.get_top_holdings().iterrows():
        top_holdings[f"holding_{i}"] = (
            f"{row['Name']} ({format_percent(row['Holding Percent'])})"
        )
        i += 1

    return basic_info | performance | sector_weighting | top_holdings
