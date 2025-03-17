import pandas as pd
from glob import glob


class FinanceData:

    def __init__(self):
        self.column_names = ["date", "transaction_type", "asset_name",
                             "quantity", "total_value"]
        self.dataframe = pd.concat([self.add_nubank_data(),
                                    self.add_trading212_data()])

    def add_nubank_data(self):
        xls_files = glob("assets/nubank_statements/*.xlsx")
        nubank_column_names = [
            "entry_type", "date", "transaction_type",  "asset_name",
            "quantity", "unit_price", "total_value"
        ]
        df_list = (pd.read_excel(io=file,
                                 engine="openpyxl",
                                 usecols="A:D,F:H",
                                 names=nubank_column_names,
                                 parse_dates=[1],
                                 na_values="-",
                                 date_format="%d/%m/%Y") for file in xls_files)
        nubank_df = pd.concat(df_list, ignore_index=True)
        nubank_df["asset_name"] = nubank_df.asset_name.str.split(" - ").str[0]

        # standardise transactions
        nubank_df.replace(to_replace={
            "Credito": "money_in",
            "Debito": "money_out",
            # bonds
            "Compra": "purchase",
            "Resgate": "sale",
            "Venda": "sale",
            "Cobrança de Taxa Semestral": "fee",
            # shares
            "Dividendo": "dividend",
            "Juros Sobre Capital Próprio": "dividend",
            "Desdobro": "split",
            "Bonificação em Ativos": "split",
            "Fração em Ativos": "split",
            # combine shares
            "ITSA1": "ITSA3",
            "ITSA2": "ITSA3",
            "ITSA4": "ITSA3",
            "ISAE3": "TRPL3",
            "LOGG3": "MRVE3",
        }, inplace=True)
        nubank_df["transaction_type"] = nubank_df.transaction_type.mask(
            cond=(nubank_df.entry_type == "money_in") &
                 (nubank_df.transaction_type == "Transferência - Liquidação"),
            other="purchase"
        )
        nubank_df["transaction_type"] = nubank_df.transaction_type.mask(
            cond=(nubank_df.entry_type == "money_out") &
                 (nubank_df.transaction_type == "Transferência - Liquidação"),
            other="sale"
        )

        # assign negative value to purchase and fees
        nubank_df.loc[
            (nubank_df.transaction_type == "purchase")
            | (nubank_df.transaction_type == "fee"), "total_value"
        ] = -1 * nubank_df.total_value

        # filter relevant transactions
        nubank_df = nubank_df.loc[
            (nubank_df.transaction_type == "purchase")
            | (nubank_df.transaction_type == "sale")
            | (nubank_df.transaction_type == "dividend")
            | (nubank_df.transaction_type == "fee")
            | (nubank_df.transaction_type == "split")
        ]

        return nubank_df[self.column_names]

    def add_trading212_data(self):
        csv_files = glob("assets/trading212_statements/*.csv")
        df_list = (pd.read_csv(
            filepath_or_buffer=file,
            parse_dates=[1],
            date_format="ISO8601",
            header=0,
            usecols=[0, 1, 4],
            names=["transaction_type", "date", "total_value"]
        ) for file in csv_files)
        trading_df = pd.concat(df_list, ignore_index=True)

        trading_df.replace(to_replace={
            "Interest on cash": "dividend",
            "Deposit": "purchase",
            "Withdrawal": "sale",
        }, inplace=True)

        trading_df["quantity"] = trading_df.total_value
        trading_df["asset_name"] = "cash ISA"

        trading_df.loc[
            (trading_df.transaction_type == "purchase")
            | (trading_df.transaction_type == "sale"), "total_value"
        ] = -1 * trading_df.total_value

        return trading_df[self.column_names]
