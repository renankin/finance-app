import pandas
from shares import Shares
import matplotlib.pyplot as plt

file_path = "assets/balance.xlsx"
df = pandas.read_excel(file_path, engine="openpyxl")

shares = Shares(df)
dividends = shares.calculate_yearly_dividend(ticker="CPLE3")
purchase = shares.calculate_yearly_purchase()
current_asset = shares.calculate_share_value()
# TODO: asset list needs to be inverted
print(shares.years)
plt.plot(shares.years, current_asset)
plt.show()
