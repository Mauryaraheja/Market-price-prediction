#Main engine - this is a production level engine (runs everything)
from utils import (is_swing_high , is_swing_low ,
                   calculate_sma , calculate_macd,
                   calculate_bollinger_bands)
from strategy import check_trade
import pandas as pd

import yfinance as yf

df = yf.download("AAPL", period="2y", interval="1d")

# 🔥 Fix MultiIndex issue
if isinstance(df.columns, tuple) or hasattr(df.columns, 'levels'):
    df.columns = df.columns.get_level_values(0)

# 🔥 Drop NaN
df = df.dropna()

# 🔥 Now rename safely
df.columns = [col.lower() for col in df.columns]

# Keep required columns
df = df[['open', 'high', 'low', 'close']]

# Convert to list of dicts
data = df.to_dict('records')

trades = []
last_swing_low = None
print(data[0])

sma = calculate_sma(data, period=20)
#Calculate MACD - returns two lists : macd_line and signal_line
macd_line , signal_line = calculate_macd(data)

#calculate Bollinger Bands - returns three lists 
upper_band , middle_band , lower_band = calculate_bollinger_bands(data,period=20)

def evaluate_trade(data, entry_index, entry, stop_loss, target):

    for i in range(entry_index + 1, len(data)):

        high = data[i]['high']
        low = data[i]['low']

        if low <= stop_loss:
            return "LOSS"

        if high >= target:
            return "WIN"

    # 🔥 NEW: force close at last candle
    final_close = data[-1]['close']

    if final_close > entry:
        return "WIN"
    else:
        return "LOSS"

i = 0

while i < len(data):

    # update swing low first
    if is_swing_low(data, i):
        last_swing_low = data[i]['low']

    # Trend filter
    if sma[i] is None or data[i]['close'] < sma[i]:
      i += 1
      continue

    #Check swing high
    if is_swing_high(data , i):
        print("Swing high found at index:",i)
        swing_high = data[i]['high']

        #Use previous swing low
        if last_swing_low is None : #No SL No trade
            i += 1
            continue

        trade = check_trade(data,i,swing_high,last_swing_low,
                            macd_line, signal_line,
                            upper_band,middle_band,lower_band)

        if trade:

            print("Trade found at index:",i)

            #Evaluate trade
            result = evaluate_trade(
                data,
                trade["entry_index"],
                trade["entry"],
                trade["stop_loss"],
                trade["target"]
            )
            trade["result"] = result
            trade["swing_high"] = swing_high
            trade["swing_low"] = last_swing_low
            trade["index"] = i
            trades.append(trade)

            #Important : skip to exit point
            i = trade["entry_index"] + 1 # this prevents overlap
            continue

    i += 1


total_trades = len(trades)

wins = sum(1 for t in trades if t["result"] == "WIN")
losses = sum(1 for t in trades if t["result"] == "LOSS")

win_rate = (wins/total_trades)*100 if total_trades > 0 else 0

print("Total trades:",total_trades)
print("Wins:",wins)
print("Losses:",losses)
print("Win rate:",win_rate)

#win rate matters , we can still be in profit if win rate is less
#because we designed are system in such a manner , reward to risk ratio is 2

total_R = 0

for t in trades:
    if t["result"] == "WIN":
        total_R += 2 #2R gain

    elif t["result"] == "LOSS":
        total_R -= 1 #1R loss

print("Total profit (R):",total_R)

# ============================================
# PERFORMANCE METRICS
# ============================================

# Step 1 — Build a list of R values for each trade
# +2 for a win, -1 for a loss
r_values = []

for t in trades:
    if t["result"] == "WIN":
        r_values.append(2)   # win = +2R
    else:
        r_values.append(-1)  # loss = -1R

# r_values is now something like: [2, -1, 2, 2, -1, -1, 2]


# Step 2 — Calculate Max Drawdown
# We go through cumulative R values and track the biggest drop

cumulative_r = []   # running total of R after each trade
running_total = 0   # starts at 0

for r in r_values:
    running_total += r          # add this trade's R to running total
    cumulative_r.append(running_total)

# cumulative_r might look like: [2, 1, 3, 5, 4, 3, 5]
# this shows how our account grew/shrank after each trade

peak = cumulative_r[0]          # start peak at first value
max_drawdown = 0                # start max drawdown at 0

for value in cumulative_r:

    if value > peak:
        peak = value
        # found a new highest point — update peak

    drawdown = peak - value
    # drawdown = how much we dropped from the peak

    if drawdown > max_drawdown:
        max_drawdown = drawdown
        # found a bigger drawdown — update max drawdown


# Step 3 — Calculate Sharpe Ratio
# Formula: average R / standard deviation of R

average_r = sum(r_values) / len(r_values)
# average R per trade
# example: [2,-1,2,-1,2] → sum=4, len=5 → average=0.8

squared_diffs = []
for r in r_values:
    diff = r - average_r        # how far is this R from average
    squared_diffs.append(diff ** 2)   # square it

variance = sum(squared_diffs) / len(squared_diffs)
# variance = average of squared differences

std_dev = variance ** 0.5
# standard deviation = square root of variance

if std_dev == 0:
    sharpe_ratio = 0
    # avoid dividing by zero if all trades have same result
else:
    sharpe_ratio = average_r / std_dev
    # higher = better quality returns


# Step 4 — Print all metrics
print("=" * 40)
print("PERFORMANCE METRICS")
print("=" * 40)
print(f"Total Trades   : {total_trades}")
print(f"Wins           : {wins}")
print(f"Losses         : {losses}")
print(f"Win Rate       : {round(win_rate, 2)}%")
print(f"Total R        : {total_R}")
print(f"Max Drawdown   : {max_drawdown}R")
print(f"Sharpe Ratio   : {round(sharpe_ratio, 2)}")


# ============================================
# CSV EXPORT
# ============================================

# Step 5 — Export trade log to CSV
# We use pandas to convert our trades list into a table

import pandas as pd
# pandas is already imported at top of your file
# but we write it here just as a reminder

# Convert trades list into a DataFrame
# each trade dictionary becomes one row
trades_df = pd.DataFrame(trades)
# trades_df now looks like a table with columns:
# entry | stop_loss | target | result | swing_high | swing_low | index

# Round all number columns to 2 decimal places (cleaner to read)
trades_df = trades_df.round(2)

# Save to CSV file
trades_df.to_csv("trade_log.csv", index=False)
# index=False means don't add row numbers as a column
# this creates a file called trade_log.csv in your project folder

print("=" * 40)
print("Trade log saved to trade_log.csv ✅")
print("=" * 40)



