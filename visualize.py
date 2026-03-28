"""
visualize.py — Phase 6: Plot Linear Regression Results
Run this after linear_model.py to see what your model actually learned.
"""

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from features import build_features, get_feature_columns
from linear_model import (
    load_data, prepare_data, split_data, train, evaluate,
    TRAIN_RATIO
)
from sklearn.linear_model import LinearRegression


def plot_results(results: dict, feat_df: pd.DataFrame):
    split      = int(len(feat_df) * TRAIN_RATIO)
    test_dates = feat_df.index[split : split + len(results["y_test"])]
    y_test     = results["y_test"]
    y_pred     = results["y_pred"]

    fig = plt.figure(figsize=(16, 10), facecolor="#0d1117")
    gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.35)

    title_kw = dict(color="#e6edf3", fontsize=12, fontweight="bold", pad=10)
    ax_kw    = dict(facecolor="#161b22")

    # ── Plot 1: Predicted vs Actual Prices ──────────────────────────────────
    ax1 = fig.add_subplot(gs[0, :], **ax_kw)
    ax1.plot(test_dates, y_test, color="#58a6ff", linewidth=1.2, label="Actual Close")
    ax1.plot(test_dates, y_pred, color="#f78166", linewidth=1.0,
             linestyle="--", alpha=0.85, label="Predicted Close")
    ax1.set_title("Actual vs Predicted Close Price (Test Set)", **title_kw)
    ax1.legend(facecolor="#21262d", edgecolor="#30363d", labelcolor="#e6edf3")
    ax1.tick_params(colors="#8b949e")
    ax1.spines[:].set_color("#30363d")
    ax1.set_ylabel("Price ($)", color="#8b949e")

    # ── Plot 2: Residuals ────────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1, 0], **ax_kw)
    residuals = y_test - y_pred
    ax2.bar(test_dates, residuals,
            color=np.where(residuals >= 0, "#3fb950", "#f78166"),
            width=1.0, alpha=0.8)
    ax2.axhline(0, color="#8b949e", linewidth=0.8, linestyle="--")
    ax2.set_title("Residuals (Actual − Predicted)", **title_kw)
    ax2.tick_params(colors="#8b949e")
    ax2.spines[:].set_color("#30363d")
    ax2.set_ylabel("Error ($)", color="#8b949e")

    # ── Plot 3: Scatter (Actual vs Predicted) ────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 1], **ax_kw)
    ax3.scatter(y_test, y_pred, color="#58a6ff", alpha=0.4, s=10)
    mn, mx = min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())
    ax3.plot([mn, mx], [mn, mx], color="#f78166", linewidth=1.2, linestyle="--", label="Perfect fit")
    ax3.set_title("Actual vs Predicted (Scatter)", **title_kw)
    ax3.set_xlabel("Actual ($)", color="#8b949e")
    ax3.set_ylabel("Predicted ($)", color="#8b949e")
    ax3.tick_params(colors="#8b949e")
    ax3.spines[:].set_color("#30363d")
    ax3.legend(facecolor="#21262d", edgecolor="#30363d", labelcolor="#e6edf3")

    # ── Metrics box ──────────────────────────────────────────────────────────
    metrics_text = (
        f"RMSE: ${results['rmse']:.4f}\n"
        f"MAE:  ${results['mae']:.4f}\n"
        f"R²:   {results['r2']:.4f}\n"
        f"Dir Acc: {results['directional_accuracy']:.2f}%"
    )
    fig.text(0.5, 0.01, metrics_text, ha="center", va="bottom",
             color="#e6edf3", fontsize=10,
             bbox=dict(boxstyle="round", facecolor="#21262d", edgecolor="#30363d", pad=0.6))

    plt.suptitle("Phase 6 — Linear Regression Baseline  |  AAPL",
                 color="#e6edf3", fontsize=14, fontweight="bold", y=1.01)

    plt.savefig("lr_results.png", dpi=150, bbox_inches="tight",
                facecolor="#0d1117")
    print("  Chart saved → lr_results.png")
    plt.show()


if __name__ == "__main__":
    df                               = load_data()
    X, y, feat_df                    = prepare_data(df)
    X_train, X_test, y_train, y_test = split_data(X, y)
    model, scaler                    = train(X_train, y_train)
    results                          = evaluate(model, scaler, X_test, y_test, feat_df)
    plot_results(results, feat_df)
