prices = [95, 100, 98, 102, 105, 103, 108]
window = 3

def calculate_sma(prices,window):
  sma_values = []

  for i in range(len(prices)-window+1):
    window_prices = prices[i:i+window]
    sma = sum(window_prices)/window
    sma_values.append(round(sma,2))

  return sma_values

sma_values = calculate_sma(prices,window)
recent = prices[-window:]
support = min(recent)
resistance = max(recent)

current_price = prices[-1]
current_sma = sma_values[-1]

if current_sma > current_price:
  trend = 'DOWNTREND'
else :
  trend = 'UPTREND'

#as we know in this case it is uptrend as current_price > current_sma
#support/resistance shows price

if current_price > current_sma and current_price <=support :
  print('Strong Buy') #as market is bullish

elif current_price < current_sma and current_price >= resistance :
  print('Strong Sell') # as market is bearish

elif current_price > current_sma :
  print('Weak Buy')

elif current_price < current_sma :
  print('Weak Sell')

else :
  print('No trade')
