from asset_analyser import AssetAnalyser
from finance_data import FinanceData
import pandas as pd
from utils import *

finance_data = FinanceData().create_df()
assets = finance_data.asset_name.unique()

combined_cashflow = pd.DataFrame()
for asset_code in assets:
    tax_due = get_tax_flag(asset_code)
    asset = AssetAnalyser(finance_data, asset_name=asset_code, currency="GBP",
                          tax_due=tax_due)
    asset_cashflow = asset.cashflow()
    combined_cashflow = pd.concat([combined_cashflow, asset_cashflow],
                                  ignore_index=True)

initial_date = finance_data.date.min()
cashflow_values = combined_cashflow.total_value.to_list()
periods = ((combined_cashflow.date - initial_date).dt.days / 365).to_list()
print(calculate_irr(cashflow_values, periods))
