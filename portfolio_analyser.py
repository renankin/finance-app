from asset_analyser import AssetAnalyser
from finance_data import FinanceData
from utils import *


class PortfolioAnalyser(FinanceData):

    def __init__(self):
        super().__init__()

    def get_irr(self) -> float:
        cashflows = []
        time_periods = []
        for asset in self.dataframe.asset_name.unique():
            asset_analyser = AssetAnalyser(
                asset_name=asset,
                tax_due=get_tax_flag(asset))
            time_periods += asset_analyser.get_cashflow_periods(
                self.dataframe.date.min()
            )
            cashflows += asset_analyser.get_cashflows()
        return calculate_irr(cashflows, time_periods)

    def get_net_value(self) -> float:
        net_value = 0
        for asset in self.dataframe.asset_name.unique():
            asset_analyser = AssetAnalyser(
                asset_name=asset,
                tax_due=get_tax_flag(asset))

            if asset_analyser.get_quantity_available() != 0:
                net_value += (
                        asset_analyser.get_quantity_available() *
                        asset_analyser.get_closing_price()
                        - asset_analyser.get_tax_value()
                )
        return net_value
