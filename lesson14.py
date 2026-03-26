#simple moving average
# prices = [100,105,102]
# average = sum(prices)/len(prices)
#
# print(average)

# prices = [100,105,102,110,115,108]
#
# last_3_prices = prices[-3:]
# sma_3 = sum(last_3_prices)/len(last_3_prices)
#
# print('Last 3 prices : ',last_3_prices)
# print('3-Day SMA: ',sma_3)
#
# print(prices[1:3])


prices = [100,105,102,110,115,108]

window = 3
#valid window - it means how many time it will calculate sma
#it will calculate sma 4 times as there are 6 elements

for i in range(len(prices)-window+1):
  window_prices = prices[i:i+window]     #as everytime it will pick 3 elements , thus in first case i=0:3 , it will run only till 2nd element not 3rd index
  sma = sum(window_prices)/window
  print('Prices:',window_prices,'SMA:',sma)

current_price = prices[-1]

if current_price > sma :
  print('Price above sma -> Bullish')
else :
  print('Price below sma -> bearish')



# using functions
# prices = [120, 118, 115, 110, 105]
# window = 3
#
# def calculate_sma(prices,count):
#   for i in range(len(prices)-count+1):
#     window_prices = prices[i:i+count]
#     sma = sum(window_prices)/count
#     print('Prices:',window_prices,'SMA',round(sma,2))
#
#
#
# calculate_sma(prices,window)


#
# prices = [120, 118, 115, 110, 105]
# window = 3
#
# def calculate_sma(prices, window):
#     sma_values = [] #it is empty , it only iniatilized
#
#     for i in range(len(prices)-window+1):
#         window_prices = prices[i:i+window]
#         sma = sum(window_prices)/window
#         sma_values.append(round(sma,2))
#
#     return sma_values
#
# result = calculate_sma(prices,window)
# print(result)
