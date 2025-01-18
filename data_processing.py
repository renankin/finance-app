import pandas as pd
from glob import glob


def create_dataframe() -> pd.DataFrame:
    """
    Creates a standardised pandas DataFrame for finance analysis.
    """
    xls_files = glob("assets" + "/*.xlsx")
    column_names = ["entry_type", "date", "transaction_type", "asset_name",
                    "quantity", "unit_price", "total_value"]
    df_list = (pd.read_excel(io=file,
                             engine="openpyxl",
                             usecols="A:D,F:H",
                             names=column_names,
                             parse_dates=[1],
                             na_values="-",
                             date_format="%d/%m/%Y") for file in xls_files)
    new_df = pd.concat(df_list, ignore_index=True)
    new_df["asset_code"] = new_df.asset_name.str.split(" - ").str[0]

    # standardise transactions
    new_df.replace(to_replace={
        "Credito": "money_in",
        "Debito": "money_out",
        # bonds
        "Compra": "purchase",
        "Resgate": "sale",
        "Cobrança de Taxa Semestral": "fee",
        # shares
        "Dividendo": "dividend",
        "Juros Sobre Capital Próprio": "dividend",
        "Leilão de Fração": "dividend",
        # combine shares
        "ITSA1": "ITSA3",
        "ITSA2": "ITSA3",
        "ITSA4": "ITSA3",
        "ISAE3": "TRPL3",
        "LOGG3": "MRVE3",
    }, inplace=True)

    new_df["transaction_type"] = new_df.transaction_type.mask(
        cond=(new_df.entry_type == "money_in") &
             (new_df.transaction_type == "Transferência - Liquidação"),
        other="purchase"
    )

    new_df["transaction_type"] = new_df.transaction_type.mask(
        cond=(new_df.entry_type == "money_out") &
             (new_df.transaction_type == "Transferência - Liquidação"),
        other="sale"
    )

    # assign negative value to purchase and fees
    new_df.loc[
        (new_df.transaction_type == "purchase") |
        (new_df.transaction_type == "fee"), "total_value"
    ] = -1 * new_df.total_value

    # filter relevant transactions
    new_df = new_df.loc[(new_df.transaction_type == "purchase")
                        | (new_df.transaction_type == "sale")
                        | (new_df.transaction_type == "dividend")
                        | (new_df.transaction_type == "fee")]

    return new_df
