#SMA + conditional code

prices = [120,118,115,110,105]
window = 3

def calculate_sma(prices,window):
  sma_values = []

  for i in range(len(prices)-window+1): #we call this sliding window rule
    window_price = prices[i:i+window]
    sma = sum(window_price)/window
    sma_values.append(round(sma,2))

  return sma_values


sma_values = calculate_sma(prices,window)
current_price = prices[-1]
latest_sma = sma_values[-1]

recent_prices = prices[-window:]
support = min(recent_prices)
resistance = max(recent_prices)

if current_price > latest_sma and current_price <= support:
    print("Strong Buy 🟢 (Uptrend + Near Support)")

elif current_price < latest_sma and current_price >= resistance:
    print("Strong Sell 🔴 (Downtrend + Near Resistance)")

elif current_price > latest_sma:
    print("Weak Buy ⚪ (Uptrend only)")

elif current_price < latest_sma:
    print("Weak Sell ⚪ (Downtrend only)")

else:
    print("No Trade ➖")