import pandas as pd


class Shares:

    def __init__(self, dataframe):
        self.data = dataframe
        self.data["Year"] = pd.to_datetime(
            self.data["Data"], format="%d/%m/%Y"
        ).dt.year
        self.years = self.data["Year"].unique()
        self.data["Ticker"] = self.data["Produto"].str.split(" - ").str[0]
        self.credit = self.data[self.data["Entrada/Saída"] == "Credito"]

    def calculate_yearly_dividend(self, ticker=False):
        """

        :param ticker: share ticker, if not provided it will
            return the sum of all shares.
        :return: Sum of dividends and JSCP per year
        """
        dividend = self.credit.query(
            'Movimentação == "Dividendo" or Movimentação == "Juros Sobre '
            'Capital Próprio"'
        )
        if ticker:
            dividend = dividend.query(f'Ticker == "{ticker}"')
        sum_dividend = []
        for year in self.years:
            dividend_per_year = dividend[dividend["Year"] == year]
            sum_dividend.append(dividend_per_year["Valor da Operação"].sum())
        return sum_dividend

    def calculate_yearly_purchase(self, ticker=False):
        purchase = self.credit[
            self.credit["Movimentação"] == "Transferência - Liquidação"
        ]
        if ticker:
            purchase = purchase.query(f'Ticker == "{ticker}"')
        yearly_purchase = []
        for year in self.years:
            purchase_per_year = purchase[purchase["Year"] == year]
            yearly_purchase.append(purchase_per_year["Valor da "
                                                     "Operação"].sum())
        return yearly_purchase

    def calculate_share_value(self):
        yearly_purchase = self.calculate_yearly_purchase()
        total_purchase = 0
        share_value = []
        for purchase in yearly_purchase:
            total_purchase += purchase
            share_value.append(total_purchase)
        return share_value
    