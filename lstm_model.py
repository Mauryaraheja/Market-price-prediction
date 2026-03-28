"""
lstm_model.py — Phase 7 (Improved): Multi-feature LSTM
Same structure as before — only input shape changes from (60,1) to (60,4)
"""

import numpy as np
import matplotlib.pyplot as plt
import os

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

from data_prep import prepare_lstm_data, N_FEATURES


# ── Config ───────────────────────────────────────────────────────────────────
SEQ_LEN    = 60
EPOCHS     = 50
BATCH_SIZE = 32
MODEL_PATH = "models/lstm_model.keras"


# ── Build Model ──────────────────────────────────────────────────────────────
def build_model(seq_len=SEQ_LEN, n_features=N_FEATURES):
    model = Sequential()

    model.add(LSTM(
        units=50,
        return_sequences=True,
        input_shape=(seq_len, n_features)
        # KEY CHANGE: was (seq_len, 1)
        # now (seq_len, 4) — 4 features per timestep
        # LSTM now sees Close + returns + dist_sma5 + rsi
        # for each of the 60 days in the sequence
    ))
    model.add(Dropout(0.2))

    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))

    model.add(Dense(units=25))
    model.add(Dense(units=1))

    model.compile(optimizer="adam", loss="mean_squared_error")

    print("\n[1/4] Model architecture:")
    model.summary()
    return model


# ── Train ────────────────────────────────────────────────────────────────────
def train_model(model, X_train, y_train, X_test, y_test):
    print("\n[2/4] Training LSTM...")

    early_stop = EarlyStopping(
        monitor="val_loss",
        patience=5,
        restore_best_weights=True
    )

    history = model.fit(
        X_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_data=(X_test, y_test),
        callbacks=[early_stop],
        verbose=1
    )

    print("\n      → Training complete ✓")
    return history


# ── Evaluate ─────────────────────────────────────────────────────────────────
def evaluate_model(model, X_test, y_test, scaler):
    print("\n[3/4] Evaluating...")

    y_pred_scaled = model.predict(X_test)

    # inverse_transform needs shape (rows, n_features)
    # we only predicted Close (column 0) so pad with zeros for other columns
    # then inverse transform and take only column 0
    def inverse_close(scaled_col):
        padded = np.zeros((len(scaled_col), N_FEATURES))
        padded[:, 0] = scaled_col.flatten()
        return scaler.inverse_transform(padded)[:, 0]

    y_pred = inverse_close(y_pred_scaled)
    y_real = inverse_close(y_test)

    # RMSE
    rmse = np.sqrt(np.mean((y_real - y_pred) ** 2))

    # Directional accuracy
    actual_dir = np.sign(y_real[1:] - y_real[:-1])
    pred_dir   = np.sign(y_pred[1:] - y_real[:-1])
    dir_acc    = np.mean(actual_dir == pred_dir) * 100

    print("\n" + "=" * 45)
    print("      LSTM (Multi-feature) — RESULTS")
    print("=" * 45)
    print(f"  RMSE              : ${rmse:.4f}")
    print(f"  Directional Acc.  : {dir_acc:.2f}%")
    print("=" * 45)
    print(f"\n  📊 Baselines to beat:")
    print(f"     LR RMSE            : $2.72")
    print(f"     LR Directional Acc.: 73.96%")

    if dir_acc > 73.96:
        print(f"\n  ✅ LSTM beats Linear Regression!")
    else:
        print(f"\n  ⚠️  Not there yet — but closer than before")
    print("=" * 45)

    return y_pred, y_real, rmse, dir_acc


# ── Plot ─────────────────────────────────────────────────────────────────────
def plot_results(y_real, y_pred, history):
    fig, axes = plt.subplots(1, 2, figsize=(16, 5), facecolor="#0d1117")

    ax1 = axes[0]
    ax1.set_facecolor("#161b22")
    ax1.plot(y_real, color="#58a6ff", linewidth=1.2, label="Actual Price")
    ax1.plot(y_pred, color="#f78166", linewidth=1.0,
             linestyle="--", alpha=0.9, label="LSTM Predicted")
    ax1.set_title("LSTM — Actual vs Predicted (Test Set)",
                  color="#e6edf3", fontsize=12)
    ax1.set_xlabel("Trading Days", color="#8b949e")
    ax1.set_ylabel("Price ($)", color="#8b949e")
    ax1.tick_params(colors="#8b949e")
    ax1.spines[:].set_color("#30363d")
    ax1.legend(facecolor="#21262d", edgecolor="#30363d", labelcolor="#e6edf3")

    ax2 = axes[1]
    ax2.set_facecolor("#161b22")
    ax2.plot(history.history["loss"],
             color="#58a6ff", linewidth=1.2, label="Train Loss")
    ax2.plot(history.history["val_loss"],
             color="#f78166", linewidth=1.2, label="Val Loss")
    ax2.set_title("Training Loss Over Epochs",
                  color="#e6edf3", fontsize=12)
    ax2.set_xlabel("Epoch", color="#8b949e")
    ax2.set_ylabel("Loss (MSE)", color="#8b949e")
    ax2.tick_params(colors="#8b949e")
    ax2.spines[:].set_color("#30363d")
    ax2.legend(facecolor="#21262d", edgecolor="#30363d", labelcolor="#e6edf3")

    plt.suptitle("Phase 7 — LSTM Multi-feature  |  AAPL",
                 color="#e6edf3", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig("lstm_results_v2.png", dpi=150,
                bbox_inches="tight", facecolor="#0d1117")
    print("\n  Chart saved → lstm_results_v2.png")
    plt.show()


# ── Save ─────────────────────────────────────────────────────────────────────
def save_model(model):
    os.makedirs("models", exist_ok=True)
    model.save(MODEL_PATH)
    print(f"  Model saved → {MODEL_PATH}")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    X_train, X_test, y_train, y_test, scaler, feat = prepare_lstm_data()
    model   = build_model()
    history = train_model(model, X_train, y_train, X_test, y_test)
    y_pred, y_real, rmse, dir_acc = evaluate_model(model, X_test, y_test, scaler)
    plot_results(y_real, y_pred, history)
    save_model(model)
