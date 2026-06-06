# Your first trading-focused Python script!

print("🎯 Welcome to Your Trading Journey!")
print("=" * 50)

# Variables - like setting up your trading parameters
account_balance = 50000
risk_per_trade = 0.01  # 1%
stock_price = 150.50

# Calculate position size
dollar_risk = account_balance * risk_per_trade
print(f"\nAccount Balance: ${account_balance:,.2f}")
print(f"Risk Per Trade: {risk_per_trade * 100}%")
print(f"Max Dollar Risk: ${dollar_risk:,.2f}")

# Position sizing calculation
stop_loss = 145.00
risk_per_share = stock_price - stop_loss
shares_to_buy = int(dollar_risk / risk_per_share)

print(f"\n📊 Trade Setup:")
print(f"Entry Price: ${stock_price}")
print(f"Stop Loss: ${stop_loss}")
print(f"Risk Per Share: ${risk_per_share:.2f}")
print(f"Shares to Buy: {shares_to_buy}")
print(f"Total Position: ${shares_to_buy * stock_price:,.2f}")

print("\n✅ Your Python environment is working perfectly!")
print("You're ready to become an expert trader! 📈")
