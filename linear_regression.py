# linear_regression.py
# ML model file for market price prediction
# Uses the same AAPL data as backtest.py — no double downloading

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


# ============================================
# STEP 1 — DOWNLOAD DATA
# ============================================

def get_data(ticker="AAPL", period="2y", interval="1d"):
    # Download the same stock data your backtest.py uses
    # so both files are always working on the same dataset

    df = yf.download(ticker, period=period, interval=interval)

    # Fix MultiIndex — same fix you already use in backtest.py
    if isinstance(df.columns, tuple) or hasattr(df.columns, 'levels'):
        df.columns = df.columns.get_level_values(0)

    # Drop rows with missing values
    df = df.dropna()

    # Lowercase column names — same convention as backtest.py
    df.columns = [col.lower() for col in df.columns]

    # Reset index so 'Date' becomes a regular column
    df = df.reset_index()

    return df


# ============================================
# STEP 2 — FEATURE ENGINEERING
# ============================================

def build_features(df):
    # We create 4 features the model will learn from:
    #   1. Day number     — overall time trend
    #   2. SMA 20         — 20-day average (medium trend)
    #   3. SMA 5          — 5-day average  (short trend)
    #   4. Daily return   — % change from yesterday to today

    # Feature 1: Day number (0, 1, 2, 3...)
    # The model uses this to spot long-term price drift
    df["day"] = np.arange(len(df))

    # Feature 2: 20-day Simple Moving Average
    # Same logic as calculate_sma() in your utils.py but using pandas
    # pandas .rolling(20).mean() does the same thing in one line
    df["sma_20"] = df["close"].rolling(window=20).mean()

    # Feature 3: 5-day Simple Moving Average (faster signal)
    df["sma_5"] = df["close"].rolling(window=5).mean()

    # Feature 4: Daily return — how much did price move today in %
    # .pct_change() calculates (today - yesterday) / yesterday
    # We multiply by 100 to get a percentage, e.g. 1.5 means +1.5%
    df["daily_return"] = df["close"].pct_change() * 100

    # Drop rows where any feature is NaN
    # This happens at the start before enough candles exist for SMA
    # e.g. SMA 20 needs at least 20 rows before it has a value
    df = df.dropna()

    return df


# ============================================
# STEP 3 — PREPARE X AND y
# ============================================

def prepare_xy(df):
    # X = the features the model LEARNS FROM (inputs)
    # y = what the model PREDICTS (output = next day's close price)

    # Our 4 feature columns
    feature_cols = ["day", "sma_20", "sma_5", "daily_return"]

    # X is a 2D array — shape: (number of rows, 4 features)
    X = df[feature_cols].values

    # y is the closing price we want to predict
    # shape: (number of rows,)
    y = df["close"].values

    return X, y, feature_cols


# ============================================
# STEP 4 — TRAIN AND EVALUATE THE MODEL
# ============================================

def train_model(X, y):
    # Split data — 80% for training, 20% for testing
    # shuffle=False is critical: we must keep time order intact
    # If we shuffle, the model sees future data during training (cheating!)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        shuffle=False
    )

    # Create the Linear Regression model
    model = LinearRegression()

    # .fit() = the actual training step
    # The model finds the best straight-line relationship between X and y
    model.fit(X_train, y_train)

    # Make predictions on the test set (data the model has never seen)
    y_pred = model.predict(X_test)

    return model, X_train, X_test, y_train, y_test, y_pred


# ============================================
# STEP 5 — METRICS
# ============================================

def print_metrics(model, feature_cols, y_test, y_pred):
    # RMSE — average prediction error in dollars
    # Lower is better
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # R² — how much of the price movement the model explains
    # 1.0 = perfect, 0.0 = no better than guessing the average
    r2 = r2_score(y_test, y_pred)

    print("=" * 40)
    print("LINEAR REGRESSION RESULTS")
    print("=" * 40)
    print(f"RMSE        : ${rmse:.2f}")
    print(f"R² Score    : {r2:.4f}  ({r2 * 100:.1f}% variance explained)")
    print()

    # Show what each feature contributed
    # coef_ tells us: "for every 1 unit increase in this feature,
    # the predicted price changes by this many dollars"
    print("Feature weights (coefficients):")
    for name, coef in zip(feature_cols, model.coef_):
        print(f"  {name:<16}: {coef:+.4f}")

    print(f"  {'intercept':<16}: {model.intercept_:+.4f}")
    print("=" * 40)

    return rmse, r2


# ============================================
# STEP 6 — PLOT RESULTS
# ============================================

def plot_results(df, X_train, y_test, y_pred, ticker="AAPL"):
    # Build a clean index for the test portion
    # We need to know which rows in df correspond to the test set
    split_index = len(X_train)  # where training ended

    # The test days come after the training days in the dataframe
    test_dates = df["date"].values[split_index: split_index + len(y_test)]

    plt.figure(figsize=(14, 6))

    # Plot full actual closing price history (blue line)
    plt.plot(df["date"], df["close"],
             color="steelblue", label="Actual closing price", linewidth=1.2)

    # Plot model predictions on the test set (red dashed line)
    plt.plot(test_dates, y_pred,
             color="tomato", label="Model predictions (test set)",
             linewidth=2, linestyle="--")

    # Vertical line showing the train/test split point
    plt.axvline(x=test_dates[0], color="gray", linestyle=":",
                linewidth=1.5, label="Train/test split")

    plt.title(f"{ticker} — Linear Regression Price Prediction", fontsize=14)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Closing price (USD)", fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("outputs/lr_prediction_plot.png", dpi=150)
    plt.show()
    print("Plot saved to outputs/lr_prediction_plot.png")


# ============================================
# MAIN ENTRY POINT
# ============================================

def run_prediction(ticker="AAPL"):
    # This function is called from main.py
    # It runs the full ML pipeline end to end

    print(f"\nRunning Linear Regression on {ticker}...\n")

    # Step 1 — get data
    df = get_data(ticker=ticker)

    # Step 2 — build features
    df = build_features(df)

    # Step 3 — prepare X and y
    X, y, feature_cols = prepare_xy(df)

    # Step 4 — train and get predictions
    model, X_train, X_test, y_train, y_test, y_pred = train_model(X, y)

    # Step 5 — print metrics
    rmse, r2 = print_metrics(model, feature_cols, y_test, y_pred)

    # Step 6 — plot
    plot_results(df, X_train, y_test, y_pred, ticker=ticker)

    return model, rmse, r2


# If you run this file directly (python linear_regression.py),
# it will execute run_prediction() automatically
if __name__ == "__main__":
    run_prediction()
