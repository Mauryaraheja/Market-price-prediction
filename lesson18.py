#Pandas
import pandas as pd

prices = [100, 102, 101, 99, 98]
window = 3

df = pd.DataFrame({
    'price':prices
})

window = 3

df['Support'] = df['price'].rolling(window).min()
df['Resistance'] = df['price'].rolling(window).max()

latest_price = df['price'].iloc[-1]
support = df['Support'].iloc[-1]
resistance = df['Resistance'].iloc[-1]
df['SMA_3'] = df["price"].rolling(window).mean()

#finding ema
df['EMA'] = df['price'].emw(span=3 , adjust = False).mean() #basically span is window

if latest_price <= support:
  print('Signal:Buy')
elif latest_price <= resistance :
  print('Signal:Sell')
else :
  print('Signal:Hold')

print(df)