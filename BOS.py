#BOS(Break of structure) , CHoCH(Change of character)
trend = "UPTREND"  # or DOWNTREND / FORMING
confirmed_highs = [(2, 105), (6, 108)]
confirmed_lows = [(4, 101), (8, 104)]

current_price = 100

last_confirmed_high = confirmed_highs[-1][1]
last_confirmed_low = confirmed_lows[-1][1]

if trend == 'UPTREND':

    if current_price > last_confirmed_high:
        signal = "BOS_UP"

    elif current_price < last_confirmed_low:
        signal = "CHoCH"

    else:
        signal = "NO EVENT"


elif trend == 'DOWNTREND':

    if current_price < last_confirmed_high:
        signal = "BOS_DOWN"

    elif current_price > last_confirmed_low:
        signal = "CHoCH"

    else:
        signal = "NO EVENT"

else:
    signal = "NO STRUCTURE"

print('Signal:', signal)