from data_processing import create_dataframe
from investiment_analyser import InvestimentAnalyser


df = create_dataframe()

asset_df = df.loc[df.asset_code == "Tesouro Prefixado 2027"]
investment_analyser = InvestimentAnalyser(cash_flow=asset_df)

print(investment_analyser.value_invested)
print(investment_analyser.return_value)
