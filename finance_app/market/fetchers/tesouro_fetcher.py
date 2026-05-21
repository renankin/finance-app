import datetime as dt
import requests


def get_prices(bond_symbol: str) -> list[dict]:
    """
    Scrape "Tesouro Transparente" portal and return daily prices for bond.
    """

    url = (
        "https://www.tesourotransparente.gov.br/ckan/dataset/"
        "df56aa42-484a-4a59-8184-7676580c81e3/resource/"
        "796d2059-14e9-44e3-80c9-2d9e30b405c1/download/"
        "precotaxatesourodireto.csv"
    )

    r = requests.get(url)

    r.raise_for_status()

    prices = []

    i = 0
    for line in r.iter_lines():
        items = line.decode("utf-8").split(";")

        # Items are: bond_name, due_date, base_date, purchase_rate, sell_rate, 
        # purchase_price, sell_price and base_price

        if i > 0:  # Skip header
            bond_name = items[0]
            maturity = dt.datetime.strptime(items[1], "%d/%m/%Y")

            if bond_symbol == f"{bond_name} {maturity.year}":
                base_date = dt.datetime.strptime(items[2], "%d/%m/%Y")
                base_price = float(items[7].replace(",", "."))

                prices.append({"date": base_date.date(), "price": base_price})

        i += 1

    return prices
