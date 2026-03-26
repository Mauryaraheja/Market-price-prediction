today = int(input("Enter today's price: "))
yesterday = int(input("Enter yesterday's price: "))

if today > yesterday:
    print("Market Trend: UP → Buy")
elif today < yesterday:
    print("Market Trend: DOWN → Wait")
else:
    print("Market Trend: SAME → Hold")
