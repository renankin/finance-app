from bs4 import BeautifulSoup
from scipy import optimize
import numpy
import requests


def calculate_npv(irr, cash_flows, years) -> float:
    return sum(cash_flows / (1 + irr) ** years)


def calculate_irr(cash_flow_values, years_run):
    solver = optimize.root(fun=calculate_npv,
                           x0=numpy.array(0),
                           args=(cash_flow_values, years_run))

    return 100 * solver.x[0]


def save_bonds_data(save_path):
    print("Updating bonds price csv file...")
    url = ("https://www.tesourotransparente.gov.br/temas/"
           "/divida-publica-federal/tesouro-direto")
    contents = requests.get(url).text
    soup = BeautifulSoup(contents, "html.parser")
    csv_url = soup.select(
        selector="a[aria-label='Download']")[1].get("href")
    response = requests.get(csv_url)
    with open(save_path, "w") as file:
        for line in response.iter_lines():
            file.write(line.decode("utf-8") + "\n")


def get_tax_flag(asset_name) -> bool:
    if "Tesouro" not in asset_name or "ISA" in asset_name:
        return False
    return True
