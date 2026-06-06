import yfinance as yf
print("Testing yfinance...")
try:
    spy = yf.download("SPY", period="1d", progress=False)
    print(f"SPY Price: {spy['Close'].iloc[-1]}")
    qqq = yf.download("QQQ", period="1d", progress=False)
    print(f"QQQ Price: {qqq['Close'].iloc[-1]}")
    print("SUCCESS - yfinance is working!")
except Exception as e:
    print(f"ERROR: {e}")
