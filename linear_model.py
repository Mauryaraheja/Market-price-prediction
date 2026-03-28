"""
linear_model.py — Phase 6: Linear Regression Model
Trains, evaluates, and saves a Linear Regression on the features from features.py.

What you'll learn here:
  - Train/test split WITHOUT data leakage (time-based, not random)
  - Scaling features (StandardScaler)
  - Fitting LinearRegression from scikit-learn
  - Evaluating: MSE, RMSE, MAE, R², Directional Accuracy
  - Saving the model with joblib (reuse in FastAPI — Phase 8)
"""

import numpy as np
import pandas as pd
import yfinance as yf
import joblib
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from features import build_features, get_feature_columns


# ── Config ─────────────────────────────────────────────────────────────────
TICKER      = "AAPL"
PERIOD      = "5y"        # 5 years of daily data
TRAIN_RATIO = 0.80        # 80% train, 20% test
MODEL_DIR   = "models"
MODEL_PATH  = os.path.join(MODEL_DIR, "lr_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "lr_scaler.pkl")


# ── Step 1: Download Data ───────────────────────────────────────────────────
def load_data(ticker: str = TICKER, period: str = PERIOD) -> pd.DataFrame:
    print(f"\n[1/5] Downloading {ticker} data ({period})...")
    df = yf.download(ticker, period=period, auto_adjust=True)
    df.dropna(inplace=True)
    print(f"      → {len(df)} candles loaded  ({df.index[0].date()} to {df.index[-1].date()})")
    return df


# ── Step 2: Build Features ──────────────────────────────────────────────────
def prepare_data(df: pd.DataFrame):
    print("\n[2/5] Engineering features...")
    feat_df = build_features(df)
    feature_cols = get_feature_columns()

    X = feat_df[feature_cols].values
    y = feat_df["target"].values

    print(f"      → {X.shape[1]} features  |  {len(y)} samples")
    return X, y, feat_df


# ── Step 3: Train/Test Split (TIME-BASED — never shuffle time series!) ──────
def split_data(X: np.ndarray, y: np.ndarray, train_ratio: float = TRAIN_RATIO):
    print(f"\n[3/5] Splitting data  (train={int(train_ratio*100)}% / test={int((1-train_ratio)*100)}%)...")
    split = int(len(X) * train_ratio)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    print(f"      → Train: {len(X_train)} samples  |  Test: {len(X_test)} samples")
    return X_train, X_test, y_train, y_test


# ── Step 4: Scale + Train ───────────────────────────────────────────────────
def train(X_train: np.ndarray, y_train: np.ndarray):
    print("\n[4/5] Scaling features and training Linear Regression...")

    # Fit scaler ONLY on train data (never on test — that's data leakage)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    model = LinearRegression()
    model.fit(X_train_scaled, y_train)

    print("      → Model trained ✓")
    return model, scaler


# ── Step 5: Evaluate ────────────────────────────────────────────────────────
def evaluate(model, scaler, X_test: np.ndarray, y_test: np.ndarray, feat_df: pd.DataFrame):
    print("\n[5/5] Evaluating on test set...")

    X_test_scaled = scaler.transform(X_test)   # use scaler fit on train only
    y_pred        = model.predict(X_test_scaled)

    # Regression metrics
    mse  = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae  = mean_absolute_error(y_test, y_pred)
    r2   = r2_score(y_test, y_pred)

    # Directional accuracy — did we predict UP or DOWN correctly?
    # Compare predicted direction vs actual direction relative to previous close
    split        = len(feat_df) - len(y_test)
    prev_close   = feat_df["Close"].values[split - 1 : -1]   # close before each test candle
    actual_dir   = np.sign(y_test  - prev_close)
    pred_dir     = np.sign(y_pred  - prev_close)
    dir_accuracy = np.mean(actual_dir == pred_dir) * 100

    print("\n" + "=" * 45)
    print("       LINEAR REGRESSION — RESULTS")
    print("=" * 45)
    print(f"  RMSE              : ${rmse:.4f}")
    print(f"  MAE               : ${mae:.4f}")
    print(f"  R² Score          : {r2:.4f}  (1.0 = perfect)")
    print(f"  Directional Acc.  : {dir_accuracy:.2f}%  (50% = random guess)")
    print("=" * 45)

    if dir_accuracy > 55:
        print("  ✅ Model beats random guessing on direction")
    else:
        print("  ⚠️  Model struggles with direction — expected for LR")
    print("  ℹ️  This is your BASELINE. LSTM will aim to beat this.\n")

    return {
        "rmse": round(rmse, 4),
        "mae":  round(mae, 4),
        "r2":   round(r2, 4),
        "directional_accuracy": round(dir_accuracy, 2),
        "y_pred": y_pred,
        "y_test": y_test,
    }


# ── Save Model ──────────────────────────────────────────────────────────────
def save_model(model, scaler):
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model,  MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"  Model  saved → {MODEL_PATH}")
    print(f"  Scaler saved → {SCALER_PATH}")


# ── Load Model (for inference / FastAPI Phase 8) ────────────────────────────
def load_model():
    model  = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    return model, scaler


# ── Predict single row (used later in FastAPI) ──────────────────────────────
def predict_next_close(model, scaler, latest_features: np.ndarray) -> float:
    """Pass in a single row of features, get predicted next close price."""
    scaled = scaler.transform(latest_features.reshape(1, -1))
    return float(model.predict(scaled)[0])


# ── Main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df                            = load_data()
    X, y, feat_df                 = prepare_data(df)
    X_train, X_test, y_train, y_test = split_data(X, y)
    model, scaler                 = train(X_train, y_train)
    results                       = evaluate(model, scaler, X_test, y_test, feat_df)
    save_model(model, scaler)
