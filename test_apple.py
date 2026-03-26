import yfinance as yf

# =========================
# 🔹 LOAD DATA
# =========================
data = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
data.columns = data.columns.droplevel(1)

# =========================
# 🔹 VARIABLES
# =========================
last_swing_high = None
breakout_level = None
retest_done = False
in_trade = False

entry_price = 0
stop_loss = 0
target = 0

wins = 0
losses = 0
total_profit = 0

# =========================
# 🔹 MAIN LOOP
# =========================
for i in range(2, len(data)):

    # Current candle values
    current_open = data["Open"].iloc[i]
    current_close = data["Close"].iloc[i]
    current_low = data["Low"].iloc[i]
    current_high = data["High"].iloc[i]

    # =========================
    # 🔹 SWING HIGH DETECTION
    # =========================
    left = data["High"].iloc[i-2]
    middle = data["High"].iloc[i-1]
    right = data["High"].iloc[i]

    if middle > left and middle > right:
        if not in_trade and breakout_level is None:
            last_swing_high = middle

    # =========================
    # 🔹 ENTRY LOGIC
    # =========================
    if not in_trade:

        # STEP 1: BREAKOUT
        if breakout_level is None and last_swing_high is not None:
            if current_close > last_swing_high:
                breakout_level = last_swing_high
                retest_done = False
                #print("Breakout on", data.index[i])

        # STEP 2: RETEST
        if breakout_level is not None and not retest_done:
            if current_low <= breakout_level * 1.02:
                #print("Retest on", data.index[i])
                retest_done = True

                # STEP 3: CONFIRMATION
                if current_close > current_open:
                    entry_price = current_close
                    stop_loss = current_low - 1
                    risk = entry_price - stop_loss
                    target = entry_price + 2 * risk

                    in_trade = True
                    breakout_level = None

                    print("BUY on", data.index[i])
                    #print("Entry:", entry_price, "SL:", stop_loss, "Target:", target)

                else:
                    # Retest failed → reset
                    breakout_level = None
                    retest_done = False
                    last_swing_high = None

    # =========================
    # 🔹 TRADE TRACKING
    # =========================
    else:

        # STOP LOSS
        if current_low <= stop_loss:
            loss = entry_price - stop_loss
            total_profit -= loss
            losses += 1

            print("LOSS on", data.index[i], "Loss:", loss)

            in_trade = False
            retest_done = False
            breakout_level = None
            last_swing_high = None

        # TARGET
        elif current_high >= target:
            profit = target - entry_price
            total_profit += profit
            wins += 1

            print("PROFIT on", data.index[i], "Profit:", profit)

            in_trade = False
            retest_done = False
            breakout_level = None
            last_swing_high = None


# =========================
# 🔹 RESULTS
# =========================
total_trades = wins + losses

print("\nTotal Trades:", total_trades)
print("Wins:", wins)
print("Losses:", losses)

if total_trades > 0:
    win_rate = (wins / total_trades) * 100
    print("Win Rate:", win_rate, "%")

print("Total Profit:", total_profit)