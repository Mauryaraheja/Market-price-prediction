#multiple functions
def price_difference(today,yesterday):
    return today - yesterday

def detect_trend(diff):
    if diff > 0:
        return 'UP'
    elif diff <0:
        return 'DOWN'
    else :
        return 'SAME'

def market_decision(trend):
    if trend == 'UP':
        return 'BUY'
    elif trend == 'DOWN':
        return 'WAIT'
    else :
        return 'HOLD'

diff = price_difference(120,80)
trend = detect_trend(diff)
decision = market_decision(trend)

print('Market',trend)
print('Decision',decision)
