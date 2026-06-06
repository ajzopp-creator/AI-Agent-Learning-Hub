import yfinance as yf

print("Fetching SPY...")
spy = yf.download("SPY", period="1d", progress=False)
spy_price = spy['Close'].iloc[-1]
print(f"SPY: ${spy_price:.2f}")

print("Fetching QQQ...")
qqq = yf.download("QQQ", period="1d", progress=False)
qqq_price = qqq['Close'].iloc[-1]
print(f"QQQ: ${qqq_price:.2f}")

print("SUCCESS - Yahoo Finance is working!")
