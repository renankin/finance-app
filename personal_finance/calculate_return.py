from datetime import datetime
import numpy as np
import pandas as pd
from scipy import optimize


def compute_irr(group_df, initial_guess=0.1):
    """
    Returns the internal rate of return (IRR) for the dataframe.
    """

    cashflow_values = group_df["Valor da Operação"]
    years_since_purchase = group_df["Anos Decorridos"]

    # IRR is found when the sum of net present value equals 0
    solver = optimize.root(
        lambda irr: sum(cashflow_values / (1 + irr) ** years_since_purchase),
        x0=initial_guess,
    )

    if not solver.success:
        return np.nan

    return solver.x[0]


def calculate_irr_for_assets(cashflow_df, prices_df):
    """
    Returns a dataframe with the internal rate of return for each asset.
    """

    # Locate latest asset prices
    prices = prices_df.sort_values("Data").groupby("Produto").last()
    names = cashflow_df["Produto"].unique()
    prices = prices.loc[names]

    # Find current amount of assets and total value
    amounts = cashflow_df.sort_values("Data").groupby("Produto").last()
    values = amounts["Quantidade Acumulada"] * prices["PU Venda Manha"]

    asset_initial_dates = cashflow_df.groupby("Produto")["Data"].min()

    # Create cashflow entries for each asset
    today = datetime.now()
    new_entries = pd.DataFrame(
        {
            "Data": today,
            "Anos Decorridos": (today - asset_initial_dates).dt.days / 365.0,
            "Valor da Operação": values,
        }
    ).reset_index()

    # Merge dataframes
    cashflow_df = pd.concat([cashflow_df, new_entries], ignore_index=True)

    # Create new dataframe by calculating IRR for each asset
    irr_from_assets = (
        cashflow_df.groupby("Produto")
        .apply(compute_irr, include_groups=False)
        .reset_index(name="IRR")
    )

    # compute IRR for the entire portfolio
    total_irr = pd.DataFrame(
        {"Produto": "Total", "IRR": [compute_irr(cashflow_df)]})

    return pd.concat([irr_from_assets, total_irr], ignore_index=True).set_index(
        "Produto"
    )
