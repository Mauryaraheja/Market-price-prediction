"""
features.py — Phase 6: Feature Engineering
Converts raw OHLCV data + your existing indicators into an ML-ready feature matrix.
Uses the same indicator functions already in utils.py.
"""

import pandas as pd
import numpy as np


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Input:  df with columns [Open, High, Low, Close, Volume]
    Output: df with all features + target variable added
    
    Target: next candle's Close price (regression target)
    """
    feat = df.copy()

    # ── 1. Price-derived features ──────────────────────────────────────────
    feat["returns"]       = feat["Close"].pct_change()              # % daily return
    feat["log_returns"]   = np.log(feat["Close"] / feat["Close"].shift(1))
    feat["hl_range"]      = feat["High"] - feat["Low"]              # candle range
    feat["body"]          = feat["Close"] - feat["Open"]            # candle body
    feat["upper_wick"]    = feat["High"] - feat[["Open", "Close"]].max(axis=1)
    feat["lower_wick"]    = feat[["Open", "Close"]].min(axis=1) - feat["Low"]

    # ── 2. SMA features (replicate calculate_sma from utils.py) ───────────
    for window in [5, 10, 20, 50]:
        feat[f"sma_{window}"] = feat["Close"].rolling(window).mean()

    # Distance from price to each SMA (normalised) — more useful than raw SMA
    for window in [5, 10, 20, 50]:
        feat[f"dist_sma_{window}"] = (feat["Close"] - feat[f"sma_{window}"]) / feat[f"sma_{window}"]

    # ── 3. EMA features ────────────────────────────────────────────────────
    for span in [12, 26]:
        feat[f"ema_{span}"] = feat["Close"].ewm(span=span, adjust=False).mean()

    # ── 4. MACD (replicate calculate_macd from utils.py) ──────────────────
    ema12 = feat["Close"].ewm(span=12, adjust=False).mean()
    ema26 = feat["Close"].ewm(span=26, adjust=False).mean()
    feat["macd"]        = ema12 - ema26
    feat["macd_signal"] = feat["macd"].ewm(span=9, adjust=False).mean()
    feat["macd_hist"]   = feat["macd"] - feat["macd_signal"]

    # ── 5. Bollinger Bands (replicate calculate_bollinger_bands) ──────────
    bb_window = 20
    bb_std    = 2
    bb_mid    = feat["Close"].rolling(bb_window).mean()
    bb_sigma  = feat["Close"].rolling(bb_window).std()
    feat["bb_upper"]    = bb_mid + bb_std * bb_sigma
    feat["bb_lower"]    = bb_mid - bb_std * bb_sigma
    feat["bb_width"]    = (feat["bb_upper"] - feat["bb_lower"]) / bb_mid   # volatility proxy
    feat["bb_position"] = (feat["Close"] - feat["bb_lower"]) / (feat["bb_upper"] - feat["bb_lower"])  # 0–1

    # ── 6. RSI ─────────────────────────────────────────────────────────────
    rsi_period = 14
    delta      = feat["Close"].diff()
    gain       = delta.clip(lower=0).rolling(rsi_period).mean()
    loss       = (-delta.clip(upper=0)).rolling(rsi_period).mean()
    rs         = gain / (loss + 1e-9)
    feat["rsi"] = 100 - (100 / (1 + rs))

    # ── 7. Volume features ─────────────────────────────────────────────────
    feat["vol_sma20"]   = feat["Volume"].rolling(20).mean()
    feat["vol_ratio"]   = feat["Volume"] / (feat["vol_sma20"] + 1e-9)      # relative volume
    feat["obv"]         = (np.sign(feat["Close"].diff()) * feat["Volume"]).cumsum()

    # ── 8. Lag features (give the model "memory") ─────────────────────────
    for lag in [1, 2, 3, 5]:
        feat[f"close_lag_{lag}"] = feat["Close"].shift(lag)
        feat[f"return_lag_{lag}"] = feat["returns"].shift(lag)

    # ── 9. Target Variable ─────────────────────────────────────────────────
    # Predict the NEXT candle's closing price
    feat["target"] = feat["Close"].shift(-1)

    # Drop rows with NaN (caused by rolling windows and lags)
    feat.dropna(inplace=True)

    return feat


def get_feature_columns() -> list:
    """Returns the list of feature column names used as X."""
    return [
        "returns", "log_returns", "hl_range", "body", "upper_wick", "lower_wick",
        "dist_sma_5", "dist_sma_10", "dist_sma_20", "dist_sma_50",
        "macd", "macd_signal", "macd_hist",
        "bb_width", "bb_position",
        "rsi",
        "vol_ratio", "obv",
        "close_lag_1", "close_lag_2", "close_lag_3", "close_lag_5",
        "return_lag_1", "return_lag_2", "return_lag_3", "return_lag_5",
    ]
