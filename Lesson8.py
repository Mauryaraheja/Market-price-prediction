#now we gonna talk about list
#list stores multiple values in single variable

# prices = [120,140,150,60]
#
# for price in prices :
#     print(price)

#price variable is created by python automatically
#but in while loop user have to create variable by user

# prices = [90, 110, 105, 130]
#
# for price in prices:
#     if price > 100:
#         print(price, "→ No Buy")
#     else:
#         print(price, "→ Buy")

#now we will compare consecutive days


prices = [100,105,98,110]

for i in range (1,len(prices)):
    if prices[i] > prices[i-1]:
        print('Day ',i,' up')
    elif prices[i] < prices[i-1]:
        print('Day ',i,' down')
    else :
        print('Same price')

