from scipy import optimize
import datetime as dt

from finance_app.assets import repository as assets
from finance_app.transactions import repository as transactions
from finance_app.market import repository as market


def adjust_transactions(asset_id: int) -> list:
    """Adjust cashflow for assets when there are stock splits and returns a list of
    dictionaries containing `date`, `shares`, `price`, `currency` and `adjusted`."""

    t = transactions.get_transactions_from_asset(asset_id)

    splits = market.get_splits_for_asset(asset_id)

    for transaction in t:
        transaction["adjusted"] = "No"
        for split in splits:
            if transaction["date"] <= split["date"]:
                transaction["shares"] *= split["split_ratio"]
                transaction["price"] /= split["split_ratio"]
                transaction["adjusted"] = "Yes"

    return t


def get_dividends_received(asset_id: int) -> list:
    """Get the dividends received for asset. Returns a list of dictionaries
    containing `date`, `amount_received` and `currency`."""

    divs = market.get_dividends_for_asset(asset_id)

    t = transactions.get_transactions_from_asset(asset_id)

    dividends = []

    for div in divs:
        # Find how many stocks we had on that dividend date
        shares = 0
        div_received = False
        for transaction in t:
            if transaction["date"] <= div["date"]:
                div_received = True
                shares += transaction["shares"]
                currency = transaction["currency"]

        if div_received:
            value = shares * div["dividend_value"]
            dividends.append(
                {"date": div["date"], "amount_received": value, "currency": currency}
            )

    return dividends


def get_irr_for_asset(asset_id: int) -> float | None:
    """Returns the internal rate of return (IRR) for asset by computing transactions,
    dividends and current valuation if position is still open.
    If holding period is less than a year returns `None`."""

    t = adjust_transactions(asset_id)

    cashflow = []
    dates = []
    total_shares = 0
    for transaction in t:
        cashflow.append(-1 * transaction["price"] * transaction["shares"])
        dates.append(transaction["date"])
        total_shares += transaction["shares"]

    dividends = get_dividends_received(asset_id)
    if dividends:
        for div in dividends:
            cashflow.append(div["amount_received"])
            dates.append(div["date"])

    a = assets.get_asset_by_id(asset_id)
    if a["still_open"]:
        prices = market.get_prices_for_asset(asset_id)
        if prices:
            price_date = max([price["date"] for price in prices])
            price_value = [
                price["unit_price"] for price in prices if price["date"] == price_date
            ]
            cashflow.append(price_value[0] * total_shares)
            dates.append(price_date)
        else:
            return None

    elapsed_years = [(date - min(dates)).days / 365 for date in dates]
    holding_period = (dt.datetime.now().date() - min(dates)).days
    if holding_period < 365:
        return None
    else:
        return compute_irr(cashflow, elapsed_years)


def compute_irr(
    transaction_values: list, elapsed_time: list, initial_guess=0
) -> float | None:
    """
    Returns the internal rate of return (IRR).
    `transaction_values` need to be negative for purchases and negative for sales.
    `elapsed_time` is the difference between first purchase and subsequent
    transactions in years.
    """

    # IRR is found when the sum of net present value equals 0
    solver = optimize.root(
        lambda irr: sum(transaction_values / (1 + irr) ** elapsed_time),
        x0=initial_guess,
    )

    if not solver.success:
        print(solver.message)
        return None

    return solver.x[0]
