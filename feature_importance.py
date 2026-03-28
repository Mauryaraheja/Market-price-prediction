"""
feature_importance.py — Phase 6: Which features actually matter?
Extracts and ranks coefficients from the trained Linear Regression.
This tells you WHICH indicators have the most predictive power.
The same analysis will guide which features you pass to LSTM in Phase 7.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from linear_model import load_data, prepare_data, split_data, train
from features import get_feature_columns


def analyze_importance():
    # Train fresh (or load saved model)
    df                               = load_data()
    X, y, feat_df                    = prepare_data(df)
    X_train, X_test, y_train, y_test = split_data(X, y)
    model, scaler                    = train(X_train, y_train)

    feature_names = get_feature_columns()
    coefficients  = model.coef_

    # Sort by absolute coefficient value
    importance_df = pd.DataFrame({
        "feature":     feature_names,
        "coefficient": coefficients,
        "abs_coef":    np.abs(coefficients),
    }).sort_values("abs_coef", ascending=False)

    print("\n" + "=" * 50)
    print("   FEATURE IMPORTANCE (by |coefficient|)")
    print("=" * 50)
    for _, row in importance_df.iterrows():
        bar   = "█" * int(row["abs_coef"] / importance_df["abs_coef"].max() * 30)
        sign  = "+" if row["coefficient"] >= 0 else "-"
        print(f"  {row['feature']:22s}  {sign}  {bar}")
    print("=" * 50)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 8), facecolor="#0d1117")
    ax.set_facecolor("#161b22")

    colors = ["#3fb950" if c >= 0 else "#f78166" for c in importance_df["coefficient"]]
    bars   = ax.barh(importance_df["feature"], importance_df["coefficient"], color=colors, alpha=0.85)

    ax.axvline(0, color="#8b949e", linewidth=0.8, linestyle="--")
    ax.set_title("Feature Coefficients — Linear Regression\n(Green = positive effect on price, Red = negative)",
                 color="#e6edf3", fontsize=12, pad=12)
    ax.tick_params(colors="#8b949e", labelsize=9)
    ax.spines[:].set_color("#30363d")
    ax.set_xlabel("Coefficient Value", color="#8b949e")

    plt.tight_layout()
    plt.savefig("lr_feature_importance.png", dpi=150,
                bbox_inches="tight", facecolor="#0d1117")
    print("\n  Chart saved → lr_feature_importance.png")
    plt.show()

    # Key insight printout
    top3 = importance_df.head(3)["feature"].tolist()
    print(f"\n  💡 Top 3 most influential features: {top3}")
    print("     → These are the features to prioritise in your LSTM (Phase 7)\n")

    return importance_df


if __name__ == "__main__":
    analyze_importance()
