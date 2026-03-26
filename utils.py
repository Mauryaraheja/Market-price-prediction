#utils file - small reusable tools
def is_strong_bullish_candle(candle):
    open_price = candle['open']
    close_price = candle['close']
    high_price = candle['high']
    low_price = candle['low']

    if close_price <= open_price :
        return False

    body = close_price - open_price
    candle_range = high_price - low_price

    if candle_range == 0:
        return False

    if body>= 0.5*candle_range:
        return True

    return False

def is_swing_high(data,i):
    #Make sure index is valid

    if i<1 or i>len(data)-2:
        return False

    if(
        data[i]['high'] > data[i-1]['high'] and
        data[i]['high'] > data[i+1]['high']
    ):
        return True

    return False


def is_swing_low(data, i):
    if i < 1 or i > len(data) - 2:
        return False

    if (
            data[i]['low'] < data[i - 1]['low'] and
            data[i]['low'] < data[i + 1]['low']
    ):
        return True

    return False

def calculate_sma(data,period=20):
    sma =[]

    for i in range(len(data)):
        if i < period :
            sma.append(None)
            continue

        total = 0
        for j in range(i-period,i):
            total += data[j]['close']

        average = total/period
        sma.append(average)

    return sma

#No adding filters to avoid choppy market 
def calculate_ema(data, period):
    # EMA = Exponential Moving Average
    # data = list of dicts with 'close' key
    # period = how many candles to use (e.g. 12, 26, 9)

    ema = []  # this list will store EMA value for every candle

    multiplier = 2 / (period + 1)
    # multiplier controls how much weight we give to recent prices
    # e.g. for period 12 → multiplier = 2/13 = 0.1538
    # higher multiplier = more weight to recent price

    for i in range(len(data)):

        if i < period - 1:
            # not enough candles yet to calculate EMA
            # so we store None as a placeholder
            ema.append(None)
            continue

        if i == period - 1:
            # first EMA value = simple average of first 'period' candles
            # this is called the "seed" value
            first_avg = sum(data[j]['close'] for j in range(period)) / period
            ema.append(first_avg)
            continue

        # for all candles after the seed:
        # EMA = (today's close × multiplier) + (yesterday's EMA × (1 - multiplier))
        todays_ema = (data[i]['close'] * multiplier) + (ema[i - 1] * (1 - multiplier))
        ema.append(todays_ema)

    return ema
    # returns a list like [None, None, ..., 172.3, 173.1, ...]


def calculate_macd(data):
    # MACD uses 3 EMA calculations:
    # Step 1 → EMA of 12 periods (fast line)
    # Step 2 → EMA of 26 periods (slow line)
    # Step 3 → MACD Line = EMA12 - EMA26
    # Step 4 → Signal Line = EMA9 of MACD Line

    ema12 = calculate_ema(data, 12)
    # fast EMA — reacts quickly to price changes

    ema26 = calculate_ema(data, 26)
    # slow EMA — reacts slowly to price changes

    macd_line = []
    # this will store MACD Line value for every candle

    for i in range(len(data)):

        if ema12[i] is None or ema26[i] is None:
            # if either EMA is not ready yet, MACD is also not ready
            macd_line.append(None)
            continue

        # MACD Line = fast EMA minus slow EMA
        # positive value = fast EMA above slow EMA = bullish momentum
        # negative value = fast EMA below slow EMA = bearish momentum
        macd_line.append(ema12[i] - ema26[i])

    # Now calculate Signal Line = EMA9 of MACD Line
    # But calculate_ema() expects list of dicts with 'close' key
    # So we convert macd_line into that format temporarily
    macd_as_dicts = []

    for val in macd_line:
        if val is None:
            macd_as_dicts.append({'close': 0})
            # placeholder — we won't use these None values anyway
        else:
            macd_as_dicts.append({'close': val})

    signal_line = calculate_ema(macd_as_dicts, 9)
    # signal line = smoothed version of MACD line

    return macd_line, signal_line
    # we return both lines as two separate lists


def calculate_bollinger_bands(data, period=20):
    # Bollinger Bands tell us how volatile the market is
    # and where price is relative to its average
    # period = how many candles to look back (default 20)

    upper_band = []   # list to store upper band values
    middle_band = []  # list to store middle band (SMA) values
    lower_band = []   # list to store lower band values

    for i in range(len(data)):

        if i < period - 1:
            # not enough candles yet
            # store None as placeholder for all three bands
            upper_band.append(None)
            middle_band.append(None)
            lower_band.append(None)
            continue

        # Step 1 — collect last 'period' closing prices
        closes = []
        for j in range(i - period + 1, i + 1):
            closes.append(data[j]['close'])
        # closes is now a list of last 20 closing prices
        # example: [171.2, 172.4, 170.8, ...]

        # Step 2 — calculate the average (middle band = SMA)
        average = sum(closes) / period

        # Step 3 — calculate standard deviation
        # Formula: sqrt of (average of squared differences from mean)

        squared_differences = []
        for close in closes:
            difference = close - average
            # how far is this price from the average?

            squared = difference ** 2
            # we square it to make all values positive
            # ** means "to the power of" in Python

            squared_differences.append(squared)

        avg_squared = sum(squared_differences) / period
        # average of all squared differences

        std_dev = avg_squared ** 0.5
        # square root of avg_squared = standard deviation
        # ** 0.5 means square root in Python

        # Step 4 — calculate the three bands
        middle = average
        upper = average + (2 * std_dev)  # 2 standard deviations above
        lower = average - (2 * std_dev)  # 2 standard deviations below

        middle_band.append(middle)
        upper_band.append(upper)
        lower_band.append(lower)

    return upper_band, middle_band, lower_band
    # returns three separate lists
    # example index 50: upper=185.2, middle=178.4, lower=171.6