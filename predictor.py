"""
predictor.py — Phase 8: Model Loader and Predictor

This file is the bridge between your saved models and the API.
It loads the trained Linear Regression model and runs predictions
on the latest downloaded AAPL data.

Why a separate file?
  - main.py handles HTTP requests (the waiter)
  - predictor.py handles the actual ML work (the kitchen)
  - Keeping them separate makes the code clean and easy to maintain
"""

import numpy as np
import pandas as pd
import yfinance as yf
import joblib
import os

from sklearn.preprocessing import StandardScaler


# ── Config ───────────────────────────────────────────────────────────────────
MODEL_PATH  = "models/lr_model.pkl"
SCALER_PATH = "models/lr_scaler.pkl"


# ── Feature columns — same order as training ─────────────────────────────────
# This MUST match get_feature_columns() in features.py exactly
# If the order is different, predictions will be garbage
FEATURE_COLS = [
    "returns", "log_returns", "hl_range", "body", "upper_wick", "lower_wick",
    "dist_sma_5", "dist_sma_10", "dist_sma_20", "dist_sma_50",
    "macd", "macd_signal", "macd_hist",
    "bb_width", "bb_position",
    "rsi",
    "vol_ratio", "obv",
    "close_lag_1", "close_lag_2", "close_lag_3", "close_lag_5",
    "return_lag_1", "return_lag_2", "return_lag_3", "return_lag_5",
]


# ── Step 1: Load the saved model and scaler ───────────────────────────────────
def load_model():
    """
    Loads the trained Linear Regression model and scaler from disk.
    These were saved in Phase 6 by linear_model.py → save_model()

    Returns:
        model  — the trained LinearRegression object
        scaler — the fitted StandardScaler object
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. "
            f"Run linear_model.py first to train and save the model."
        )
    if not os.path.exists(SCALER_PATH):
        raise FileNotFoundError(
            f"Scaler not found at {SCALER_PATH}. "
            f"Run linear_model.py first to train and save the scaler."
        )

    model  = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    return model, scaler


# ── Step 2: Download latest data ──────────────────────────────────────────────
def get_latest_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    Downloads the most recent price data for the given ticker.
    We only need 1 year — enough to compute all rolling indicators.

    Args:
        ticker — stock symbol e.g. "AAPL"
        period — how much history to download (default 1 year)

    Returns:
        Clean DataFrame with OHLCV columns
    """
    df = yf.download(ticker, period=period, auto_adjust=True, progress=False)

    # Fix MultiIndex columns — same fix as backtest.py
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.dropna(inplace=True)
    return df


# ── Step 3: Build features from raw data ─────────────────────────────────────
def build_features_for_prediction(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rebuilds the exact same features as features.py → build_features()
    We duplicate the logic here so predictor.py is self-contained
    and doesn't need features.py to be importable.

    Args:
        df — raw OHLCV DataFrame

    Returns:
        DataFrame with all 26 feature columns added
    """
    feat = df.copy()

    # Price features
    feat["returns"]     = feat["Close"].pct_change()
    feat["log_returns"] = np.log(feat["Close"] / feat["Close"].shift(1))
    feat["hl_range"]    = feat["High"] - feat["Low"]
    feat["body"]        = feat["Close"] - feat["Open"]
    feat["upper_wick"]  = feat["High"] - feat[["Open", "Close"]].max(axis=1)
    feat["lower_wick"]  = feat[["Open", "Close"]].min(axis=1) - feat["Low"]

    # SMA distances
    for window in [5, 10, 20, 50]:
        sma = feat["Close"].rolling(window).mean()
        feat[f"sma_{window}"]      = sma
        feat[f"dist_sma_{window}"] = (feat["Close"] - sma) / sma

    # MACD
    ema12 = feat["Close"].ewm(span=12, adjust=False).mean()
    ema26 = feat["Close"].ewm(span=26, adjust=False).mean()
    feat["macd"]        = ema12 - ema26
    feat["macd_signal"] = feat["macd"].ewm(span=9, adjust=False).mean()
    feat["macd_hist"]   = feat["macd"] - feat["macd_signal"]

    # Bollinger Bands
    bb_mid   = feat["Close"].rolling(20).mean()
    bb_sigma = feat["Close"].rolling(20).std()
    feat["bb_upper"]    = bb_mid + 2 * bb_sigma
    feat["bb_lower"]    = bb_mid - 2 * bb_sigma
    feat["bb_width"]    = (feat["bb_upper"] - feat["bb_lower"]) / bb_mid
    feat["bb_position"] = (feat["Close"] - feat["bb_lower"]) / (
                           feat["bb_upper"] - feat["bb_lower"])

    # RSI
    delta = feat["Close"].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    feat["rsi"] = 100 - (100 / (1 + gain / (loss + 1e-9)))

    # Volume
    feat["vol_sma20"] = feat["Volume"].rolling(20).mean()
    feat["vol_ratio"] = feat["Volume"] / (feat["vol_sma20"] + 1e-9)
    feat["obv"]       = (np.sign(feat["Close"].diff()) * feat["Volume"]).cumsum()

    # Lag features
    for lag in [1, 2, 3, 5]:
        feat[f"close_lag_{lag}"]  = feat["Close"].shift(lag)
        feat[f"return_lag_{lag}"] = feat["returns"].shift(lag)

    feat.dropna(inplace=True)
    return feat


# ── Step 4: Run the prediction ────────────────────────────────────────────────
def predict(ticker: str) -> dict:
    """
    Full prediction pipeline:
      1. Load model + scaler
      2. Download latest data
      3. Build features
      4. Scale features
      5. Predict next closing price
      6. Return result as a dictionary

    Args:
        ticker — stock symbol e.g. "AAPL"

    Returns:
        dict with prediction details
    """

    # Load model
    model, scaler = load_model()

    # Get data
    df = get_latest_data(ticker)
    if len(df) < 60:
        raise ValueError(f"Not enough data for {ticker}. Need at least 60 candles.")

    # Build features
    feat_df = build_features_for_prediction(df)

    # Take the LAST row — most recent trading day
    # This is the row we use to predict the NEXT day
    latest_row = feat_df[FEATURE_COLS].iloc[-1].values
    # shape: (26,) — one value per feature

    # Reshape to (1, 26) — scaler and model expect 2D array
    latest_row = latest_row.reshape(1, -1)

    # Scale using the saved scaler (same one used during training)
    latest_scaled = scaler.transform(latest_row)

    # Predict
    predicted_price = float(model.predict(latest_scaled)[0])

    # Get current price for reference
    current_price = float(feat_df["Close"].iloc[-1])
    last_date     = str(feat_df.index[-1].date())

    # Direction
    direction = "UP 📈" if predicted_price > current_price else "DOWN 📉"
    change    = predicted_price - current_price
    change_pct = (change / current_price) * 100

    return {
        "ticker":          ticker.upper(),
        "last_close_date": last_date,
        "current_price":   round(current_price, 2),
        "predicted_price": round(predicted_price, 2),
        "predicted_change": round(change, 2),
        "predicted_change_pct": round(change_pct, 2),
        "direction":       direction,
        "model":           "Linear Regression (Phase 6)",
    }
