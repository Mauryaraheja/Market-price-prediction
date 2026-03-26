# trading logic
from utils import is_strong_bullish_candle


def is_retest(data, i, level):
    # Checks if price came back to test the breakout level
    # We use a generous zone so we don't miss valid retests

    lower = level * 0.98   # 2% below the level
    upper = level * 1.02   # 2% above the level

    current_candle = data[i]

    if lower <= current_candle['low'] <= upper:
        # candle's low touched the zone = valid retest
        return True

    if lower <= current_candle['close'] <= upper:
        # candle's close is inside zone = valid retest
        return True

    return False


def macd_filter(macd_line, signal_line, i):
    # This filter checks if MACD momentum is bullish at index i
    # Rule: MACD Line must be above Signal Line

    if macd_line[i] is None or signal_line[i] is None:
        # MACD not ready yet (not enough candles)
        # we return False to skip this candle safely
        return False

    if macd_line[i] > signal_line[i]:
        # MACD line is above signal line = bullish momentum ✅
        return True

    # MACD line is below signal line = weak momentum ❌
    return False


def bollinger_filter(data, upper_band, middle_band, lower_band, i):
    # This filter checks two things:
    # 1. Price is above middle band (bullish position)
    # 2. Bands are wide enough (market is trending, not choppy)

    if upper_band[i] is None or middle_band[i] is None:
        # Bollinger Bands not ready yet
        return False

    current_close = data[i]['close']

    # Condition 1 — price must be above middle band
    if current_close < middle_band[i]:
        # price is below average = not bullish enough
        return False

    # Condition 2 — bands must be wide enough
    # we measure band width as a percentage of middle band
    band_width = (upper_band[i] - lower_band[i]) / middle_band[i]
    # example: upper=185, lower=171, middle=178
    # band_width = (185-171)/178 = 0.0786 = 7.86%

    if band_width < 0.03:
        # bands are too narrow = market is choppy/sideways
        # 0.03 means 3% — if width is less than 3% skip this trade
        return False

    # Both conditions passed = good market conditions ✅
    return True


def check_trade(data, i, swing_high, swing_low,
                macd_line, signal_line,
                upper_band, middle_band, lower_band):
    # Main function to find a trade setup
    # Now accepts macd and bollinger data as extra parameters
    # i = index of swing high candle
    # We look ahead max 15 candles

    for j in range(i + 1, min(i + 15, len(data))):

        # STEP 1 — Breakout candle
        # price must close above the swing high
        if data[j]['close'] > swing_high:

            # STEP 2 — Retest candle
            # next candle must come back and touch the level
            if j + 1 < len(data) and is_retest(data, j + 1, swing_high):

                # STEP 3 — Confirmation candle
                # must be a strong bullish candle
                if j + 2 < len(data) and is_strong_bullish_candle(data[j + 2]):

                    # STEP 4 — MACD Filter
                    # check momentum at confirmation candle
                    if not macd_filter(macd_line, signal_line, j + 2):
                        # momentum is not bullish, skip this setup
                        continue
                        # continue means go back to top of for loop
                        # and check the next candle

                    # STEP 5 — Bollinger Band Filter
                    # check market conditions at confirmation candle
                    if not bollinger_filter(data, upper_band, 
                                          middle_band, lower_band, j + 2):
                        # market is choppy or price below average
                        # skip this setup
                        continue

                    # ALL 5 STEPS PASSED — this is a valid trade ✅

                    # entry price = close of confirmation candle
                    entry_price = data[j + 2]['close']

                    # stop loss = the swing low
                    stop_loss = swing_low

                    # risk = how much we lose if stop loss is hit
                    risk = entry_price - stop_loss

                    if risk <= 0:
                        # invalid setup — entry is below stop loss
                        continue

                    # target = 2x the risk (2R)
                    target = entry_price + 2 * risk

                    return {
                        "entry": entry_price,
                        "stop_loss": stop_loss,
                        "target": target,
                        "entry_index": j + 2
                    }

    # no valid trade found in next 15 candles
    return None