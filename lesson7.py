#loops
#starting with while loop

# day = 1
# while day <= 3 :
#
#     price = int(input('Enter market price: '))
#
#     if price > 100:
#         print('High price')
#     else :
#         print('Low price')
#
#     day += 1

#daily basis pe bta rah hai price low hai ya high
#for loop is cleaner than while

for day in range(1,4):
    yesterday_price = int(input('Enter yesterday price: '))
    today_price = int(input('Enter today price: '))

    if yesterday_price > today_price:
        print('Down->Wait')
    elif yesterday_price < today_price:
        print('Up->Wait')
    else :
        print('Same ->Hold')
#this loop will run only 3 times , 4 is in open bracket