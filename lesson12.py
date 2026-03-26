prices = [80,120,90,140]

#this is recursion
def decision_for_price(price):
    if price < 100 :
        return 'Buy'
    else :
        return 'No buy'

def analyze_price(prices):
    for price in prices :
        decision = decision_for_price(price)
        print(price,'->',decision)

analyze_price(prices)
