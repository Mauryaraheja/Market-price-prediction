"""
streamlit_app.py — Market Price Prediction Dashboard
======================================================
Connects to your running FastAPI and visualizes predictions.

Install:
    pip install streamlit requests plotly

Run:
    streamlit run streamlit_app.py

Make sure your FastAPI is running first:
    py -3.11 -m uvicorn main:app --reload
"""

import streamlit as st
import requests
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Market Price Predictor",
    page_icon="📈",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #1e2130;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        border: 1px solid #2d3250;
    }
    .metric-label {
        font-size: 13px;
        color: #9da5c2;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 600;
        color: #e6edf3;
    }
    .up   { color: #3fb950; }
    .down { color: #f85149; }
    .tag  {
        display: inline-block;
        font-size: 12px;
        padding: 2px 10px;
        border-radius: 20px;
        background: #2d3250;
        color: #9da5c2;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.title("📈 Market Price Predictor")
st.caption("Powered by Linear Regression · Phase 8 FastAPI · Built from scratch")

st.divider()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    ticker = st.text_input(
        "Stock Ticker",
        value="AAPL",
        max_chars=5,
        placeholder="e.g. AAPL, TSLA, MSFT"
    ).upper().strip()

    period = st.selectbox(
        "Chart Period",
        options=["1mo", "3mo", "6mo", "1y", "2y"],
        index=2
    )

    predict_btn = st.button("🔮 Get Prediction", use_container_width=True, type="primary")

    st.divider()
    st.subheader("🔗 API Status")

    try:
        health = requests.get(f"{API_BASE}/health", timeout=3).json()
        st.success("API is online ✅")
    except:
        st.error("API is offline ❌")
        st.caption(f"Start it with:\nuvicorn main:app --reload")


# ── API Calls ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def fetch_prediction(ticker):
    r = requests.get(f"{API_BASE}/predict/{ticker}", timeout=15)
    return r.json() if r.status_code == 200 else None

@st.cache_data(ttl=60)
def fetch_model_info():
    r = requests.get(f"{API_BASE}/model/info", timeout=5)
    return r.json() if r.status_code == 200 else None

@st.cache_data(ttl=300)
def fetch_history(ticker, period):
    df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
    if isinstance(df.columns, object) and hasattr(df.columns, 'levels'):
        df.columns = df.columns.get_level_values(0)
    return df


# ── Main Content ──────────────────────────────────────────────────────────────
if predict_btn or ticker:
    with st.spinner(f"Fetching prediction for {ticker}..."):
        prediction = fetch_prediction(ticker)
        model_info = fetch_model_info()
        history    = fetch_history(ticker, period)

    if prediction is None:
        st.error(f"Could not get prediction for **{ticker}**. Check the ticker and try again.")
        st.stop()

    # ── Metric Row ─────────────────────────────────────────────────────────
    current   = prediction.get("current_price", 0)
    predicted = prediction.get("predicted_price", 0)
    change    = predicted - current
    change_pct = (change / current * 100) if current else 0
    direction = "▲" if change >= 0 else "▼"
    color     = "up" if change >= 0 else "down"
    signal    = "BUY signal" if change >= 0 else "SELL signal"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Current Price</div>
            <div class="metric-value">${current:.2f}</div>
            <div class="tag">{prediction.get('ticker', ticker)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Predicted Next Close</div>
            <div class="metric-value {color}">${predicted:.2f}</div>
            <div class="tag">{direction} {abs(change_pct):.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Expected Change</div>
            <div class="metric-value {color}">{direction} ${abs(change):.2f}</div>
            <div class="tag">{signal}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        last_date = prediction.get("last_close_date", "N/A")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Last Close Date</div>
            <div class="metric-value" style="font-size:20px">{last_date}</div>
            <div class="tag">Next trading day</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chart ──────────────────────────────────────────────────────────────
    st.subheader(f"📊 {ticker} Price History + Prediction")

    if not history.empty:
        close = history["Close"].squeeze()
        dates = history.index

        fig = go.Figure()

        # Historical price line
        fig.add_trace(go.Scatter(
            x=dates,
            y=close,
            mode="lines",
            name="Closing Price",
            line=dict(color="#58a6ff", width=1.8)
        ))

        # Prediction point
        next_day_label = "Next Day Prediction"
        fig.add_trace(go.Scatter(
            x=[dates[-1]],
            y=[predicted],
            mode="markers+text",
            name=next_day_label,
            marker=dict(
                color="#3fb950" if change >= 0 else "#f85149",
                size=12,
                symbol="diamond"
            ),
            text=[f"  ${predicted:.2f}"],
            textposition="middle right",
            textfont=dict(color="#3fb950" if change >= 0 else "#f85149", size=13)
        ))

        # Dashed connector from last close to prediction
        fig.add_trace(go.Scatter(
            x=[dates[-1], dates[-1]],
            y=[current, predicted],
            mode="lines",
            line=dict(color="#8b949e", dash="dot", width=1),
            showlegend=False
        ))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=420,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#21262d", tickprefix="$")
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"Could not load historical data for {ticker}.")

    # ── Model Metrics ──────────────────────────────────────────────────────
    if model_info:
        st.divider()
        st.subheader("🧠 Model Performance")

        metrics = model_info.get("metrics", {})
        m1, m2, m3, m4 = st.columns(4)

        m1.metric("Model",          model_info.get("model", "Linear Regression"))
        m2.metric("RMSE",           metrics.get("rmse", "—"))
        m3.metric("R² Score",       metrics.get("r2", "—"))
        m4.metric("Directional Accuracy", metrics.get("directional_accuracy", "—"))

        with st.expander("ℹ️ What do these metrics mean?"):
            st.markdown("""
| Metric | Value | Meaning |
|--------|-------|---------|
| **RMSE** | $2.72 | On average, predictions are $2.72 off from actual price |
| **R²** | 0.9229 | Model explains 92.29% of price variance — excellent |
| **Directional Accuracy** | 73.96% | Correctly predicts UP or DOWN 74% of the time (random = 50%) |
            """)

    # ── Footer ─────────────────────────────────────────────────────────────
    st.divider()
    st.caption(
        f"Data from Yahoo Finance · Trained on AAPL 5y · "
        f"Phase 6 Linear Regression · Last updated: {datetime.now().strftime('%H:%M:%S')}"
    )

else:
    st.info("👈 Enter a ticker in the sidebar and click **Get Prediction** to start.")
