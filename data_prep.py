"""
data_prep.py — Phase 7 (Improved): Multi-feature LSTM Data Preparation

Key change from v1:
  Instead of just Close price, we now feed 4 features:
    1. Close price     — the price itself
    2. Returns         — daily % change (direction signal)
    3. SMA 5 distance  — short term trend
    4. RSI             — momentum / overbought / oversold

Why this helps directional accuracy:
  - Returns directly encode UP/DOWN information
  - RSI tells the model when a reversal is likely
  - SMA distance tells the model how far price has stretched
  - Close price alone has no direction signal built in
"""

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
import joblib
import os


# ── Config ───────────────────────────────────────────────────────────────────
TICKER      = "AAPL"
PERIOD      = "5y"
SEQ_LEN     = 60
TRAIN_RATIO = 0.80
SCALER_PATH = "models/lstm_scaler.pkl"
N_FEATURES  = 4     # number of features we're feeding the LSTM


# ── Step 1: Download Data ────────────────────────────────────────────────────
def load_data(ticker=TICKER, period=PERIOD):
    print(f"[1/4] Downloading {ticker} data ({period})...")
    df = yf.download(ticker, period=period, auto_adjust=True)

    # Fix MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.dropna(inplace=True)
    print(f"      → {len(df)} candles  ({df.index[0].date()} to {df.index[-1].date()})")
    return df


# ── Step 2: Build Features ───────────────────────────────────────────────────
def build_features(df):
    print("\n[2/4] Building features...")
    feat = df.copy()

    # Feature 1: Close price (normalised later)
    # Already in df

    # Feature 2: Daily returns — % change day to day
    # This is the most direct signal for direction
    feat["returns"] = feat["Close"].pct_change()

    # Feature 3: Distance from 5-day SMA
    # Positive = price above short term average (bullish)
    # Negative = price below short term average (bearish)
    sma5 = feat["Close"].rolling(5).mean()
    feat["dist_sma5"] = (feat["Close"] - sma5) / sma5

    # Feature 4: RSI (14 period)
    # Below 30 = oversold → likely to go up
    # Above 70 = overbought → likely to go down
    delta = feat["Close"].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / (loss + 1e-9)
    feat["rsi"] = 100 - (100 / (1 + rs))

    # Drop NaN rows caused by rolling windows
    feat.dropna(inplace=True)

    print(f"      → Features: Close, returns, dist_sma5, rsi")
    print(f"      → {len(feat)} rows after dropping NaN")
    return feat


# ── Step 3: Scale Features ───────────────────────────────────────────────────
def scale_data(feat, train_ratio=TRAIN_RATIO):
    print("\n[3/4] Scaling features...")

    # Select the 4 feature columns
    feature_cols = ["Close", "returns", "dist_sma5", "rsi"]
    data = feat[feature_cols].values
    # shape: (rows, 4)

    split = int(len(data) * train_ratio)

    # Each feature needs its own scaler
    # because Close is in hundreds, RSI is 0-100, returns is tiny decimals
    # we scale each column independently to 0-1
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(data[:split])          # fit on train only
    scaled = scaler.transform(data)   # transform all

    print(f"      → Scaled {len(feature_cols)} features to 0–1 range")

    # Save scaler — needed to inverse_transform Close predictions later
    os.makedirs("models", exist_ok=True)
    joblib.dump(scaler, SCALER_PATH)
    print(f"      → Scaler saved → {SCALER_PATH}")

    return scaled, scaler, split


# ── Step 4: Create Sequences ─────────────────────────────────────────────────
def create_sequences(scaled, seq_len=SEQ_LEN):
    print(f"\n[4/4] Creating {seq_len}-day sequences...")

    X, y = [], []

    for i in range(seq_len, len(scaled)):
        # X = last 60 rows, ALL 4 features
        X.append(scaled[i - seq_len : i, :])   # shape: (60, 4)

        # y = next day's Close price only (column 0)
        y.append(scaled[i, 0])

    X = np.array(X)   # shape: (num_sequences, 60, 4)
    y = np.array(y)   # shape: (num_sequences,)

    print(f"      → X shape: {X.shape}  (sequences, timesteps, features)")
    print(f"      → y shape: {y.shape}")
    return X, y


# ── Train/Test Split ─────────────────────────────────────────────────────────
def split_sequences(X, y, split, seq_len=SEQ_LEN):
    adjusted_split = split - seq_len
    X_train, X_test = X[:adjusted_split], X[adjusted_split:]
    y_train, y_test = y[:adjusted_split], y[adjusted_split:]
    print(f"\n      → Train: {len(X_train)} sequences")
    print(f"      → Test : {len(X_test)} sequences")
    return X_train, X_test, y_train, y_test


# ── Main ─────────────────────────────────────────────────────────────────────
def prepare_lstm_data():
    df                               = load_data()
    feat                             = build_features(df)
    scaled, scaler, split            = scale_data(feat)
    X, y                             = create_sequences(scaled)
    X_train, X_test, y_train, y_test = split_sequences(X, y, split)
    return X_train, X_test, y_train, y_test, scaler, feat


if __name__ == "__main__":
    X_train, X_test, y_train, y_test, scaler, feat = prepare_lstm_data()
    print("\n✅ Data preparation complete.")
