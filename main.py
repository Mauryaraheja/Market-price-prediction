#main.py - run this to execute the full pipeline
from backtest import trades , wins , losses , win_rate , total_R
from linear_regression import run_prediction 

if __name__ == "__main__":
    print("=== Bactest Results ===")
    print(f"WIN Rate : {win_rate:2f}% | total R: {total_R}")

    print("\n=== ML Prediction ===")
    run_prediction()
