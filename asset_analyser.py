from datetime import datetime
from utils import *
import yfinance
import pandas as pd
import os
import datetime as dt
from data_processing import FinanceData


class AssetAnalyser(FinanceData):

    def __init__(self, asset_name, tax_due):
        super().__init__()
        self.asset_name = asset_name
        self.asset_df = self.dataframe.loc[
            self.dataframe.asset_name == asset_name
        ]
        self._tax_due = tax_due

    def get_quantity_available(self) -> float:
        purchased = self.asset_df.loc[
            self.asset_df.transaction_type == "purchase"
            ].quantity.sum()
        sold = self.asset_df.loc[
            self.asset_df.transaction_type == "sale"
            ].quantity.sum()
        stock_split = self.asset_df.loc[
            (self.asset_df.transaction_type == "split")
            ].quantity.sum()
        return float(abs(purchased) + abs(stock_split) - abs(sold))

    def get_net_result(self) -> float:
        purchases_sum = abs(self.asset_df.loc[
                                self.asset_df.transaction_type == "purchase"
                                ].total_value.sum())

        sales_sum = self.asset_df.loc[
            self.asset_df.transaction_type == "sale"
            ].total_value.sum()
        dividends_sum = abs(self.asset_df.loc[
                                self.asset_df.transaction_type == "dividend"
                                ].total_value.sum())

        if self.get_quantity_available() != 0:
            sales_sum += (self.get_quantity_available()
                          * self.get_closing_price())

        return float(sales_sum - purchases_sum + dividends_sum)

    def get_tax_value(self) -> float:
        if self.get_net_result() > 0 and self._tax_due:
            tax_value = 0.15 * self.get_net_result()
            return float(tax_value)
        return 0

    def get_cashflows(self) -> list:
        cashflow = self.asset_df.loc[self.asset_df.transaction_type != "split"]
        cashflow_values = cashflow.total_value.to_list()
        if self._tax_due:
            cashflow_values.append(-self.get_tax_value())
        if self.get_quantity_available() != 0:
            cashflow_values.append(
                self.get_quantity_available() * self.get_closing_price()
            )
        return cashflow_values

    def get_cashflow_periods(self, initial_date: pd.Timestamp) -> list:
        cash_flow = self.asset_df.loc[self.asset_df.transaction_type != "split"]
        time_periods = ((cash_flow.date - initial_date).dt.days / 365).to_list()
        today = datetime.now()
        if self._tax_due:
            if self.get_quantity_available() != 0:
                time_periods.append((today - initial_date).days / 365)
            else:
                sale = cash_flow.loc[cash_flow.transaction_type == "sale"]
                last_sale_date = sale.date.max()
                time_periods.append((last_sale_date - initial_date).days / 365)
        if self.get_quantity_available() != 0:
            time_periods.append((today - initial_date).days / 365)
        return time_periods

    def get_irr(self):
        return calculate_irr(self.get_cashflows(),
                             self.get_cashflow_periods(self.asset_df.date.min()))

    def get_closing_price(self) -> float:
        if "Tesouro" in self.asset_name:
            bonds_path = "assets/bonds.csv"
            try:
                filetime = dt.datetime.fromtimestamp(
                    os.path.getctime(bonds_path)
                )
                if filetime.date() != dt.datetime.now().date():
                    save_bonds_data(save_path=bonds_path)
            except FileNotFoundError:
                save_bonds_data(save_path=bonds_path)

            bonds = pd.read_csv(bonds_path, sep=';', decimal=',')
            bonds["Data Vencimento"] = pd.to_datetime(bonds["Data Vencimento"],
                                                      dayfirst=True)
            bonds["Data Base"] = pd.to_datetime(bonds["Data Base"],
                                                dayfirst=True)
            bonds_today = bonds.loc[
                bonds["Data Base"] == bonds["Data Base"].max()
            ]
            asset_year = int(self.asset_name[-4:])
            asset_name = self.asset_name[:-5]
            asset_mask = (
                    (bonds_today["Data Vencimento"].dt.year == asset_year)
                    & (bonds_today["Tipo Titulo"] == asset_name)
            )
            return bonds_today.loc[asset_mask]["PU Venda Manha"].item()

        if self.asset_name == "cash ISA":
            return 1

        history = yfinance.Ticker(f"{self.asset_name}.SA").history()
        closing_price = history["Close"].loc[history.index.max()]
        return float(closing_price)
