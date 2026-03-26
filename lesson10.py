# def add(a,b):
#     print(a+b)
#
# add(1,2)# isne sirf print kra na ki return kra
#real life ma printing se kaam nahi chlta , return bhi krna hota hai

# def sqaure(num):
#     return num*num
#
# result = sqaure(5)
# print(result)
#
# def market_decision(price):
#     if price <100:
#         return 'Buy'
#     elif price>200:
#         return 'Sell'
#     else :
#         return 'Hold'
#
# result = market_decision(100)
# print(result)

prices = [80,100,345]

def market_price(price):
    if price > 100 :
        return 'Sell'
    else :
        return 'Buy'

for price in prices :
    result = market_price(price)
    print(price,'->',result)

