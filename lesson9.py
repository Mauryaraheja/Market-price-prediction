def market_price(price):
    if price<100:
        print(price,' Purchase')
    elif price>100:
        print(price,' Sell')
    else :
        print(price,' Same')


prices = [95,120,45,130]
for price in prices :
    market_price(price)

# using loop , passing consecutive values


