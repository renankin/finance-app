import pandas
from datetime import datetime
from scipy import optimize
from utils import calculate_npv
import numpy


class InvestimentAnalyser:

    def __init__(self, cash_flow: pandas.DataFrame):
        self.cash_flow = cash_flow

        self.value_invested = -1 * self.cash_flow.loc[
            (self.cash_flow.transaction_type == "purchase") |
            (self.cash_flow.transaction_type == "fee")
        ].total_value.sum()

        self.dividend_received = self.cash_flow.loc[
            self.cash_flow.transaction_type == "dividend"
        ].total_value.sum()

        self.asset_quantity = self.find_current_amount()

        self.return_rate, self.return_value = self.calculate_return()

        self.duration = self.find_investment_duration()

    def find_current_amount(self):
        """
        Calculates the net quantity of an asset.
        """
        amount_purchased = self.cash_flow.loc[
            self.cash_flow.transaction_type == "purchase"
        ].quantity.sum()

        amount_sold = self.cash_flow.loc[
            self.cash_flow.transaction_type == "sale"
        ].quantity.sum()

        # adjust for stock splits or bonuses
        if amount_sold > amount_purchased:
            amount_purchased += amount_sold - amount_purchased
        current_amount = amount_purchased - amount_sold

        return current_amount

    def find_investment_duration(self) -> float:
        """
        Returns the duration of investment in years from the initial
        purchase.
        """
        today = datetime.now()

        first_purchase_date = self.cash_flow.loc[
            self.cash_flow.transaction_type == "purchase"
        ].date.min()

        if self.asset_quantity == 0:
            last_sold_date = self.cash_flow.loc[
                self.cash_flow.transaction_type == "sale"
            ].date.max()
            return (last_sold_date - first_purchase_date).days/365

        return (today - first_purchase_date).days/365

    def calculate_tax(self) -> float:
        """
        Calculates the tax for a given asset.
        """
        purchase_price = self.cash_flow.loc[
            self.cash_flow.transaction_type == "purchase"
        ].total_value.sum()

        sale_price = self.cash_flow.loc[
            self.cash_flow.transaction_type == "sale"
        ].total_value.sum()

        net_result = sale_price - purchase_price

        if net_result > 0:
            tax_value = 0.15 * net_result
            return tax_value

        return 0

    def calculate_return(self):
        """
        Calculates the return of investment in percentage by computing the
        internal rate of return (IRR).
        """
        if self.asset_quantity != 0:
            return 0, 0

        if "Tesouro" in self.cash_flow["asset_code"]:
            tax_value = self.calculate_tax()

            self.cash_flow.loc[
                self.cash_flow.transaction_type == "sale", "total_value"
            ] -= tax_value

        first_purchase_date = self.cash_flow.loc[
            self.cash_flow.transaction_type == "purchase"
        ].date.min()

        elapsed_years = (
            self.cash_flow.date - first_purchase_date
        ).dt.days / 365

        solver = optimize.root(
            fun=calculate_npv,
            x0=numpy.array(0),
            args=(self.cash_flow.total_value, elapsed_years)
        )

        return 100 * solver.x[0], self.cash_flow.total_value.sum()
