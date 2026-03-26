prices = [100, 102, 105, 103, 101, 104, 108, 106, 103]

swing_high =[]
swing_low =[]

for i in range(1,len(prices)-1):
    current_price = prices[i]
    prev_price = prices[i-1]
    next_price = prices[i+1]

    if current_price > prev_price and current_price > next_price:
        swing_high.append((i,current_price))

    elif current_price < prev_price and current_price < next_price:
        swing_low.append((i,current_price))


print('Swing High:',swing_high)
print('Swing Low:',swing_low)

confirmed_highs = []
confirmed_lows = []

tentative_highs = None
tentative_lows = None

for index,price in swing_high :
    if tentative_highs is None :
        tentative_highs = (index,price)

    else :
        confirmed_highs.append(tentative_highs)
        confirmed_highs.append((index,price))
        tentative_highs = (index,price)

for index,price in swing_low :
    if tentative_lows is None :
        tentative_lows = (index,price)

    else :
        confirmed_lows.append(tentative_lows)
        confirmed_lows.append((index,price))
        tentative_lows = (index,price)


if len(confirmed_highs)<2 or len(confirmed_lows)<2 :
    trend = 'FORMING'

else :
    prev_high = confirmed_highs[-2][1]
    current_high = confirmed_highs[-1][1]

    prev_low = confirmed_lows[-2][1]
    current_low = confirmed_lows[-1][1]

    if current_high > prev_high:
        trend = 'UPTREND'
    elif current_low < prev_low:
        trend = 'DOWNTREND'
    else :
        trend = 'SIDEWAYS'

print("TREND:",trend)

