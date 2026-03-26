#EMA - EXPONENTIAL MOVING AVERAGE
prices = [120,118,115,110,105]
window = 3

alpha = 2/(window+1)

ema = prices[0] #start ema from first price

for price in prices[1:]:
  ema = (price * alpha) + (ema*(1-alpha))


print('EMA:',round(ema,2))

current_price = prices[-1]

if current_price < ema :
  print('Signal:Bearish')
else :
  print('Signal:Bullish')
