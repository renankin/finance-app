from idlelib.pyparse import trans

import pandas
import matplotlib.pyplot as plt
from glob import glob

import pandas as pd


def get_asset_code(codes):
    """ Return an asset code from a list of codes """
    options = ""
    for index, code in enumerate(codes):
        options += f"{index}:{code}\n"
    print(options)
    chosen_number = input(f"Choose code to analyse (0 - {len(codes)-1}): ")
    if chosen_number:
        code = codes[int(chosen_number)]
        return code
    return codes


def calculate_cumulative_sum(df, asset_code, year_range):
    credit = df[df["Entrada/Saída"] == "Credito"]
    debit = df[df["Entrada/Saída"] == "Debito"]
    purchase_header = "Transferência - Liquidação"
    sold_header = "Transferência - Liquidação"
    if "Tesouro" in asset_code:
        purchase_header = "Compra"
        sold_header = "Resgate"

    purchased = credit[credit["Movimentação"] == purchase_header]
    sold = debit[debit["Movimentação"] == sold_header]
    purchased_yearly = get_yearly_transactions(purchased, asset_code,
                                               year_range)
    sold_yearly = get_yearly_transactions(sold, asset_code, year_range)
    yearly_transaction = [purchased_yearly[year] - sold_yearly[year] for
                          year in range(len(purchased_yearly))]

    cumulative_sum = []
    total_transaction = 0
    for transaction in reversed(yearly_transaction):
        total_transaction += transaction
        cumulative_sum.append(total_transaction)
    cumulative_sum.reverse()

    return cumulative_sum


def calculate_cumulative_portfolio(df, asset_codes, year_range):
    cumulative_sum_combined = {}
    for code in asset_codes:
        cumulative_sum = calculate_cumulative_sum(df, code, year_range)
        cumulative_sum_combined[code] = cumulative_sum

    cumulative_sum_in_assets = []
    for index in range(len(years)):
        total_transaction = 0
        for asset in cumulative_sum_combined:
            print()
            total_transaction += cumulative_sum_combined[asset][index]
        cumulative_sum_in_assets.append(total_transaction)

    return cumulative_sum_in_assets


def get_yearly_transactions(df, asset_code):
    # Filter dataframe by asset code and group by year
    asset_grouped = df.loc[df["asset_name"] == asset_code].groupby(
        df.date.dt.year)

    # Create a new dataframe with sum of transactions done per year
    transactions = {year: group["value"].sum() for (year, group)
                    in asset_grouped}

    return transactions


# Read files with pandas
xls_files = glob("assets" + "/*.xlsx")
column_names = ["entry_type", "date", "transaction", "asset_name", "value"]
df_list = (pd.read_excel(io=file,
                         engine="openpyxl",
                         usecols="A:D,H",
                         names=column_names,
                         parse_dates=[1],
                         date_format="%d/%m/%Y") for file in xls_files)
df_combined = pd.concat(df_list, ignore_index=True)

asset_codes = df_combined.asset_name.unique()

get_yearly_transactions(df_combined, asset_codes[1])

