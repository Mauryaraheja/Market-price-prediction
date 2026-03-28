"""
main.py — Phase 8: FastAPI Application

This is the waiter of your restaurant.
It defines the routes (menu) and handles requests (orders).

How to run:
    py -3.11 -m uvicorn main:app --reload

Then open in browser:
    http://127.0.0.1:8000              ← home
    http://127.0.0.1:8000/docs         ← interactive API docs (FREE, auto-generated)
    http://127.0.0.1:8000/predict/AAPL ← prediction for AAPL
    http://127.0.0.1:8000/predict/TSLA ← prediction for TSLA
"""

from fastapi import FastAPI, HTTPException
from predictor import predict


# ── Create the FastAPI app ────────────────────────────────────────────────────
app = FastAPI(
    title="Market Price Prediction API",
    description="Predicts next day closing price using Linear Regression trained on technical indicators.",
    version="1.0.0"
)
# FastAPI automatically generates interactive docs at /docs
# You don't need to write any documentation — it reads your code


# ── Route 1: Home ─────────────────────────────────────────────────────────────
@app.get("/")
def home():
    """
    @app.get("/") means:
      - when someone sends a GET request to "/"
      - run this function and return the result

    This is the home route — like the homepage of a website
    """
    return {
        "message": "Market Price Prediction API is running ✅",
        "usage":   "Go to /predict/{ticker} to get a prediction",
        "example": "/predict/AAPL",
        "docs":    "/docs"
    }


# ── Route 2: Health Check ─────────────────────────────────────────────────────
@app.get("/health")
def health():
    """
    Health check endpoint.
    Used to verify the API is alive and responding.
    In production, monitoring tools ping this every few seconds.
    """
    return {"status": "healthy"}


# ── Route 3: Predict ──────────────────────────────────────────────────────────
@app.get("/predict/{ticker}")
def get_prediction(ticker: str):
    """
    Main prediction endpoint.

    {ticker} is a path parameter — it changes with each request:
      /predict/AAPL  → ticker = "AAPL"
      /predict/TSLA  → ticker = "TSLA"
      /predict/MSFT  → ticker = "MSFT"

    FastAPI automatically:
      - extracts "AAPL" from the URL
      - passes it to this function as the ticker argument
      - converts the returned dict to JSON
    """

    # Validate ticker — must be 1 to 5 uppercase letters
    ticker = ticker.upper().strip()
    if not ticker.isalpha() or len(ticker) > 5:
        # HTTPException sends a proper error response with status code
        # 400 = Bad Request (user sent wrong input)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid ticker '{ticker}'. Use a valid stock symbol like AAPL, TSLA, MSFT."
        )

    try:
        # Call predictor.py → runs the full ML pipeline
        result = predict(ticker)
        return result

    except FileNotFoundError as e:
        # 503 = Service Unavailable (model not trained yet)
        raise HTTPException(status_code=503, detail=str(e))

    except ValueError as e:
        # 404 = Not Found (not enough data for this ticker)
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        # 500 = Internal Server Error (something unexpected broke)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# ── Route 4: Model Info ───────────────────────────────────────────────────────
@app.get("/model/info")
def model_info():
    """
    Returns information about the model being used.
    Useful for anyone consuming the API to know what powers the predictions.
    """
    return {
        "model":            "Linear Regression",
        "phase":            "Phase 6",
        "features":         26,
        "training_data":    "AAPL 5 years daily OHLCV",
        "train_test_split": "80% / 20% time-based",
        "metrics": {
            "rmse":               "$2.72",
            "r2":                 "0.9229",
            "directional_accuracy": "73.96%"
        },
        "target": "Next day closing price"
    }
