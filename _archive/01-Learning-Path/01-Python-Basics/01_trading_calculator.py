"""
My First Trading Calculator
A real Python script that does position sizing!
"""

print("=" * 60)
print("💰 POSITION SIZE CALCULATOR")
print("=" * 60)

# Get your trading parameters
account_balance = 50000
risk_percentage = 1.0  # 1% risk per trade

# Trade setup
stock_symbol = "AAPL"
entry_price = 180.50
stop_loss = 175.00

# Calculate risk
dollar_risk = account_balance * (risk_percentage / 100)
risk_per_share = entry_price - stop_loss
shares_to_buy = int(dollar_risk / risk_per_share)
total_position_value = shares_to_buy * entry_price
position_percentage = (total_position_value / account_balance) * 100

# Display results
print(f"\n📊 ACCOUNT INFO:")
print(f"   Account Balance: ${account_balance:,.2f}")
print(f"   Risk Per Trade: {risk_percentage}%")
print(f"   Dollar Risk: ${dollar_risk:,.2f}")

print(f"\n📈 TRADE SETUP - {stock_symbol}:")
print(f"   Entry Price: ${entry_price:.2f}")
print(f"   Stop Loss: ${stop_loss:.2f}")
print(f"   Risk Per Share: ${risk_per_share:.2f}")

print(f"\n✅ POSITION SIZING:")
print(f"   Shares to Buy: {shares_to_buy}")
print(f"   Total Position Value: ${total_position_value:,.2f}")
print(f"   Position as % of Account: {position_percentage:.1f}%")

print(f"\n💡 RISK ANALYSIS:")
if position_percentage > 25:
    print("   ⚠️  WARNING: Position is large! Consider reducing.")
elif position_percentage > 15:
    print("   ⚡ CAUTION: This is a significant position.")
else:
    print("   ✓ Position size looks reasonable.")

print("\n" + "=" * 60)
print("✨ This is what Python can do for your trading!")
print("=" * 60)