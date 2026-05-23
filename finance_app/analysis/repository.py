from scipy import optimize
import datetime as dt

from finance_app.assets import repository as assets
from finance_app.transactions import repository as transactions
from finance_app.market import dividends, prices, splits


def get_adjusted_transactions(asset_id: int) -> list:
    """Adjust cashflow for assets when there are stock splits and returns a list of
    dictionaries containing `date`, `shares`, `price`, `currency` and `adjusted`."""

    t = transactions.get_transactions_from_asset(asset_id)

    s = splits.get_splits_for_asset(asset_id)

    for transaction in t:
        transaction["adjusted"] = "No"
        for split in s:
            if transaction["date"] <= split["date"]:
                transaction["shares"] *= split["split_ratio"]
                transaction["price"] /= split["split_ratio"]
                transaction["adjusted"] = "Yes"

    return t


def get_return_for_assets() -> list[dict]:
    """Returns a list of dictionaries containing the return for all assets
    including `asset_name`, `currency`, `still_open`, `total_invested`,
    `total_sold`, `total_dividends`,`irr` and `net_return`"""

    all_assets = assets.get_all_assets()

    all_stats = []

    for asset in all_assets:
        divs = get_dividends_received(asset["asset_id"])
        total_divs = sum(div["amount_received"] for div in divs)

        trans = get_adjusted_transactions(asset["asset_id"])
        total_invested = sum(t["price"] * t["shares"] for t in trans if t["shares"] > 0)
        total_sold = sum(t["price"] * -t["shares"] for t in trans if t["shares"] < 0)

        market_value = 0
        if asset["still_open"]:
            p = prices.get_most_recent_price(asset["asset_id"])
            if p:
                total_shares = sum(t["shares"] for t in trans)
                market_value = total_shares * p["price"]

        total_return = market_value + total_sold + total_divs
        if total_invested > 0 and total_return > 0:
            roi = (total_return - total_invested) / total_invested
        else:
            roi = None

        stats = {
            "asset_name": asset["asset_name"],
            "still_open": asset["still_open"],
            "currency": asset["currency"],
            "total_invested": total_invested,
            "total_sold": total_sold,
            "market_value": market_value,
            "total_dividends": total_divs,
            "irr": get_irr_for_asset(asset["asset_id"]),
            "roi": roi,
        }

        all_stats.append(stats)

    return all_stats


def get_dividends_received(asset_id: int) -> list[dict]:
    """Get the dividends received for asset. Returns a list of dictionaries
    containing `date`, `amount_received` and `currency`."""

    market_divs = dividends.get_dividends_for_asset(asset_id)
    t = get_adjusted_transactions(asset_id)

    divs_received = []
    for div in market_divs:
        a = assets.get_asset_by_id(asset_id)
        if not a["still_open"]:
            last_date = max([transaction["date"] for transaction in t])
            if div["date"] >= last_date:
                continue

        # Find how many shares on that dividend date
        shares = 0
        div_received = False
        for transaction in t:
            if transaction["date"] <= div["date"]:
                div_received = True
                shares += transaction["shares"]
                currency = transaction["currency"]

        if div_received:
            value = shares * div["dividend_value"]
            divs_received.append(
                {"date": div["date"], "amount_received": value, "currency": currency}
            )

    return divs_received


def get_irr_for_asset(asset_id: int) -> float | None:
    """Returns the internal rate of return (IRR) for asset by computing transactions,
    dividends and current valuation if position is still open.
    If holding period is less than a year returns `None`."""

    t = get_adjusted_transactions(asset_id)

    if not t:
        return None

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
        p = prices.get_most_recent_price(asset_id)
        if p:
            cashflow.append(p["price"] * total_shares)
            dates.append(p["date"])
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
