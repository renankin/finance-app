from asset_analyser import AssetAnalyser
from portfolio_analyser import PortfolioAnalyser

asset_analyser = AssetAnalyser(asset_name="cash ISA",
                               tax_due=False)

portfolio_analyser = PortfolioAnalyser()

print(portfolio_analyser.get_irr())
