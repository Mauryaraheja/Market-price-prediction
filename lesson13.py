prices = [100, 105, 102, 110, 115, 108]

first_price = prices[0]
last_price = prices[-1]

if last_price > first_price:
    print('UPTREND')
elif last_price < first_price:
    print('DOWNTREND')
else :
    print('SAME')