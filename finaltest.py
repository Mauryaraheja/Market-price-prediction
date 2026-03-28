"""
Phase 9 — Final Testing Suite
==============================
Tailored for: Market Price Prediction API
Run with:    python phase9_test.py

Your API must be running first:
    py -3.11 -m uvicorn main:app --reload
"""

import requests
import json
import sys
import time

BASE_URL = "http://127.0.0.1:8000"

# ── Terminal Colors ────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

PASS_ICON = f"{GREEN}✅ PASS{RESET}"
FAIL_ICON = f"{RED}❌ FAIL{RESET}"
WARN_ICON = f"{YELLOW}⚠️  WARN{RESET}"

results = []


def log(name, passed, detail="", warn=False):
    if warn:
        icon = WARN_ICON
    else:
        icon = PASS_ICON if passed else FAIL_ICON
    print(f"  {icon}  {name}")
    if detail:
        print(f"         {CYAN}→ {detail}{RESET}")
    results.append(passed)


def section(title):
    print(f"\n{BOLD}── {title} {'─' * (50 - len(title))}{RESET}")


# ══════════════════════════════════════════════════════════════════════════════
# TEST 1 — API HEALTH
# ══════════════════════════════════════════════════════════════════════════════
section("1. API Health Check")

# Root endpoint
try:
    r = requests.get(f"{BASE_URL}/", timeout=5)
    data = r.json()
    is_running = r.status_code == 200 and "message" in data
    log("Root endpoint ( / )", is_running, data.get("message", ""))
except requests.exceptions.ConnectionError:
    print(f"\n  {RED}{BOLD}FATAL: Cannot connect to {BASE_URL}{RESET}")
    print(f"  {YELLOW}→ Make sure your API is running:{RESET}")
    print(f"    py -3.11 -m uvicorn main:app --reload\n")
    sys.exit(1)

# Health endpoint
try:
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    data = r.json()
    log("/health endpoint", r.status_code == 200, str(data))
except Exception as e:
    log("/health endpoint", False, str(e))

# Docs endpoint
try:
    r = requests.get(f"{BASE_URL}/docs", timeout=5)
    log("/docs (Swagger UI) reachable", r.status_code == 200, f"status {r.status_code}")
except Exception as e:
    log("/docs reachable", False, str(e))


# ══════════════════════════════════════════════════════════════════════════════
# TEST 2 — PREDICT ENDPOINT (Valid Tickers)
# ══════════════════════════════════════════════════════════════════════════════
section("2. Prediction Endpoint — Valid Tickers")

for ticker in ["AAPL", "TSLA", "MSFT"]:
    try:
        start = time.time()
        r = requests.get(f"{BASE_URL}/predict/{ticker}", timeout=20)
        elapsed = round(time.time() - start, 2)
        data = r.json()

        if r.status_code == 200:
            # Check for expected fields in response
            has_ticker     = "ticker" in data or ticker in str(data)
            has_prediction = any(k in data for k in [
                "predicted_price", "prediction", "next_close",
                "predicted_close", "direction"
            ])
            detail = f"{elapsed}s | response: {json.dumps(data)[:120]}"
            log(f"/predict/{ticker}", has_prediction, detail)
        else:
            log(f"/predict/{ticker}", False, f"HTTP {r.status_code} — {data}")
    except Exception as e:
        log(f"/predict/{ticker}", False, str(e))


# ══════════════════════════════════════════════════════════════════════════════
# TEST 3 — MODEL INFO ENDPOINT
# ══════════════════════════════════════════════════════════════════════════════
section("3. Model Info Endpoint")

try:
    r = requests.get(f"{BASE_URL}/model/info", timeout=5)
    data = r.json()
    has_metrics = "metrics" in data
    has_model   = "model" in data
    log("/model/info endpoint", r.status_code == 200 and has_model)
    if has_metrics:
        m = data["metrics"]
        print(f"         {CYAN}→ RMSE: {m.get('rmse')} | R²: {m.get('r2')} | Dir. Acc: {m.get('directional_accuracy')}{RESET}")
except Exception as e:
    log("/model/info endpoint", False, str(e))


# ══════════════════════════════════════════════════════════════════════════════
# TEST 4 — EDGE CASES & ERROR HANDLING
# ══════════════════════════════════════════════════════════════════════════════
section("4. Edge Cases & Error Handling")

# Invalid ticker — too long
try:
    r = requests.get(f"{BASE_URL}/predict/TOOLONGTICKER", timeout=5)
    log("Rejects ticker > 5 chars", r.status_code == 400,
        f"Got HTTP {r.status_code} (expected 400)")
except Exception as e:
    log("Rejects ticker > 5 chars", False, str(e))

# Invalid ticker — numbers
try:
    r = requests.get(f"{BASE_URL}/predict/12345", timeout=5)
    log("Rejects numeric ticker", r.status_code == 400,
        f"Got HTTP {r.status_code} (expected 400)")
except Exception as e:
    log("Rejects numeric ticker", False, str(e))

# Invalid ticker — special chars
try:
    r = requests.get(f"{BASE_URL}/predict/AA@PL", timeout=5)
    log("Rejects ticker with special chars", r.status_code in [400, 422],
        f"Got HTTP {r.status_code}")
except Exception as e:
    log("Rejects special char ticker", False, str(e))

# Lowercase ticker — should auto-uppercase
try:
    r = requests.get(f"{BASE_URL}/predict/aapl", timeout=20)
    log("Handles lowercase ticker (auto-uppercases)", r.status_code == 200,
        f"Got HTTP {r.status_code}")
except Exception as e:
    log("Handles lowercase ticker", False, str(e))


# ══════════════════════════════════════════════════════════════════════════════
# TEST 5 — RESPONSE STRUCTURE VALIDATION
# ══════════════════════════════════════════════════════════════════════════════
section("5. Response Structure Validation")

try:
    r = requests.get(f"{BASE_URL}/predict/AAPL", timeout=20)
    data = r.json()

    if r.status_code == 200:
        # Check that prediction value is a reasonable stock price
        pred_val = None
        for key in ["predicted_price", "prediction", "next_close", "predicted_close"]:
            if key in data:
                pred_val = data[key]
                break

        if pred_val is not None:
            try:
                price = float(pred_val)
                # AAPL is typically between $50 and $1000
                reasonable = 10 < price < 10000
                log("Prediction is a valid float", isinstance(price, float) or isinstance(price, int),
                    f"value = {price}")
                log("Prediction is in reasonable price range ($10–$10,000)", reasonable,
                    f"${price}")
            except (TypeError, ValueError):
                log("Prediction is a valid float", False, f"got: {pred_val}")
        else:
            # Maybe it returns direction instead
            direction_keys = [k for k in data if "direction" in k.lower() or "signal" in k.lower()]
            log("Response has prediction or direction field",
                len(direction_keys) > 0, f"keys found: {list(data.keys())}")

        # Check ticker is echoed back
        ticker_echoed = any(v == "AAPL" for v in data.values() if isinstance(v, str))
        log("Response echoes ticker symbol", ticker_echoed, str(data)[:100])

    else:
        log("Valid AAPL response structure", False, f"HTTP {r.status_code}")

except Exception as e:
    log("Response structure validation", False, str(e))


# ══════════════════════════════════════════════════════════════════════════════
# TEST 6 — PERFORMANCE / RESPONSE TIME
# ══════════════════════════════════════════════════════════════════════════════
section("6. Response Time")

try:
    times = []
    for _ in range(3):
        start = time.time()
        requests.get(f"{BASE_URL}/predict/AAPL", timeout=30)
        times.append(round(time.time() - start, 2))

    avg = round(sum(times) / len(times), 2)
    fast = avg < 5.0

    log(f"Average response time under 5s", fast,
        f"avg={avg}s over 3 calls | times={times}")

    if avg > 10:
        print(f"         {YELLOW}→ Tip: Consider caching yfinance data to speed up predictions{RESET}")
    elif avg > 5:
        print(f"         {YELLOW}→ Acceptable for now, but caching would help in production{RESET}")

except Exception as e:
    log("Response time test", False, str(e))


# ══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
total  = len(results)
passed = sum(results)
failed = total - passed

print(f"\n{'═' * 55}")
print(f"{BOLD}  PHASE 9 — FINAL TEST RESULTS{RESET}")
print(f"{'═' * 55}")
print(f"  {GREEN}Passed : {passed}/{total}{RESET}")
if failed:
    print(f"  {RED}Failed : {failed}/{total}{RESET}")
print(f"{'═' * 55}")

if failed == 0:
    print(f"\n  {GREEN}{BOLD}🎉 All tests passed! Your API is production-ready.{RESET}")
    print(f"\n  {CYAN}What's next?{RESET}")
    print("   • Deploy to Railway / Render / Fly.io")
    print("   • Add a simple frontend (React or HTML) on top of /predict")
    print("   • Add /predict/lstm route to expose your LSTM model too")
    print("   • Add rate limiting with slowapi")
    print("   • Add authentication with API keys")
elif failed <= 3:
    print(f"\n  {YELLOW}{BOLD}Almost there! Fix the {failed} failing test(s) above.{RESET}")
else:
    print(f"\n  {RED}{BOLD}Several tests failed — check your API is running correctly.{RESET}")

print()