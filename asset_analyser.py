from datetime import datetime
from utils import *
import yfinance
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
WISE_KEY = os.environ.get("WISE_KEY")


class AssetAnalyser:

    def __init__(self, finance_data, asset_name, currency="", tax_due=True):
        super().__init__()
        self.asset_name = asset_name
        self.tax_due = tax_due

        asset_data = finance_data[finance_data.asset_name == asset_name]
        self.purchases = asset_data[asset_data.transaction_type == "purchase"]
        self.sales = asset_data[asset_data.transaction_type == "sale"]
        self.split = asset_data[asset_data.transaction_type == "split"]
        self.dividends = asset_data[asset_data.transaction_type == "dividend"]

        self.source_currency = asset_data.currency.unique()[0]
        if currency:
            self.target_currency = currency
        else:
            self.target_currency = self.source_currency

    def exchange_currency(self, row):
        search_parameters = {
            "source": self.source_currency,
            "target": self.target_currency,
            "time": row.date.date(),
        }
        response = requests.get("https://api.wise.com/v1/rates",
                                headers={
                                    "Authorization": f"Bearer {WISE_KEY}"},
                                params=search_parameters)
        response.raise_for_status()
        exchange_data = response.json()
        exchange_rate = exchange_data[0]["rate"]

        row.total_value *= exchange_rate
        row.currency = self.target_currency
        return row

    def quantity(self):
        purchased = abs(self.purchases.quantity.sum())
        sold = abs(self.sales.quantity.sum())
        stock_split = abs(self.split.quantity.sum())
        return purchased + stock_split - sold

    def net_result(self):
        purchases_sum = abs(self.purchases.total_value.sum())
        sales_sum = abs(self.sales.total_value.sum())
        dividends_sum = abs(self.dividends.total_value.sum())
        if self.quantity() != 0:
            sales_sum += (self.quantity() * self.closing_price())
        return sales_sum - purchases_sum + dividends_sum

    def tax_value(self):
        if self.net_result() > 0 and self.tax_due:
            tax_value = 0.15 * self.net_result()
            return tax_value
        return 0

    def cashflow(self):
        cashflow = pd.concat([self.sales, self.dividends, self.purchases],
                             ignore_index=True)

        today = datetime.now()
        if self.tax_due:
            tax_data = {
                "date": today,
                "transaction_type": "tax",
                "asset_name": self.asset_name,
                "quantity": self.quantity(),
                "total_value": -1 * self.tax_value(),
                "currency": "BRL",
            }
            tax_df = pd.DataFrame(tax_data, index=[0])
            cashflow = pd.concat([cashflow, tax_df], ignore_index=True)

        if self.quantity() != 0:
            sale_value = self.quantity() * self.closing_price()
            sale_data = {
                "date": today,
                "transaction_type": "sale",
                "asset_name": self.asset_name,
                "quantity": self.quantity(),
                "total_value": sale_value,
                "currency": self.source_currency,
            }
            sale_df = pd.DataFrame(sale_data, index=[0])
            cashflow = pd.concat([cashflow, sale_df], ignore_index=True)

        if self.target_currency != self.source_currency:
            print(f"Converting {self.source_currency} to "
                  f"{self.target_currency} for {self.asset_name}...")
            return cashflow.apply(func=self.exchange_currency, axis=1)

        return cashflow

    def irr(self, date):
        cashflows = self.cashflow()
        cashflow_values = cashflows.total_value.to_list()
        periods = ((cashflows.date - date).dt.days / 365).to_list()
        return calculate_irr(cashflow_values, periods)

    def closing_price(self) -> float:
        if "Tesouro" in self.asset_name:
            bonds_path = "assets/bonds.csv"
            try:
                last_edited_time = os.path.getctime(bonds_path)
                time_dt = datetime.fromtimestamp(last_edited_time)
                if time_dt.date() != datetime.now().date():
                    save_bonds_data(save_path=bonds_path)
            except FileNotFoundError:
                save_bonds_data(save_path=bonds_path)

            # open csv file with bond prices and return asset price
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
        return closing_price
