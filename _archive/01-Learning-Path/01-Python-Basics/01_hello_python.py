"""
Module 1: Hello Python! 🐍
Your first Python script for AI agent development

This script teaches you the absolute basics of Python.
Every line is explained - read the comments carefully!

How to run this:
1. Open VS Code
2. Open Terminal (View → Terminal)
3. Type: python 01_hello_python.py
4. Press Enter

Author: AI Agent Learning Hub
Date: 2025-12-31
Difficulty: Beginner
"""

# ============================================
# PART 1: Hello World & Print Statements
# ============================================

# This is a comment - Python ignores these lines
# Comments help explain what your code does

# The print() function displays text
print("Hello, Future AI Agent Developer!")
print("Let's learn Python together!")

# You can print numbers too
print(42)
print(3.14)

# Print multiple things at once (separated by commas)
print("I am", 25, "years old")

# ============================================
# PART 2: Variables
# ============================================

# Variables store data
# Think of them as labeled boxes that hold information

# Creating variables (no need to declare type in Python!)
trader_name = "Your Name"  # Text (called a "string")
account_balance = 50000    # Whole number (called an "integer")
risk_per_trade = 0.02      # Decimal (called a "float")
is_trading_enabled = True  # True/False (called a "boolean")

# Print variables
print("\n--- Your Trading Profile ---")  # \n creates a new line
print("Name:", trader_name)
print("Account Balance: $", account_balance)
print("Risk Per Trade:", risk_per_trade * 100, "%")
print("Trading Enabled:", is_trading_enabled)

# ============================================
# PART 3: Math Operations
# ============================================

print("\n--- Math Operations ---")

# Basic math
addition = 10 + 5
subtraction = 10 - 5
multiplication = 10 * 5
division = 10 / 5
power = 2 ** 8  # 2 to the power of 8

print("10 + 5 =", addition)
print("10 - 5 =", subtraction)
print("10 * 5 =", multiplication)
print("10 / 5 =", division)
print("2 ** 8 =", power)

# Trading calculation example
position_size = account_balance * risk_per_trade
print("\nPosition Size (2% risk):", position_size)

# ============================================
# PART 4: Strings (Text)
# ============================================

print("\n--- Working with Strings ---")

# You can use single or double quotes
stock_symbol = "AAPL"
company_name = 'Apple Inc.'

# Combining strings (concatenation)
full_info = stock_symbol + " - " + company_name
print(full_info)

# String formatting (better way!)
# f-strings let you insert variables into text
message = f"I'm analyzing {stock_symbol} which is {company_name}"
print(message)

# Useful string methods
print("Uppercase:", stock_symbol.upper())
print("Lowercase:", stock_symbol.lower())
print("Length:", len(stock_symbol))  # Number of characters

# ============================================
# PART 5: User Input (Interactive!)
# ============================================

print("\n--- Interactive Section ---")

# Get input from the user
# (Comment this out if running in batch mode)
user_stock = input("Enter a stock symbol you want to track: ")
print(f"Great! I'll help you track {user_stock}")

# Convert input to number
shares_str = input("How many shares do you own? ")
shares = int(shares_str)  # Convert string to integer
print(f"You own {shares} shares")

# ============================================
# PART 6: If Statements (Making Decisions)
# ============================================

print("\n--- Decision Making ---")

# If statements let your code make choices
current_price = 150.50
buy_price = 145.00

if current_price > buy_price:
    profit = current_price - buy_price
    print(f"You're in profit! Up ${profit} per share")
elif current_price < buy_price:
    loss = buy_price - current_price
    print(f"Currently down ${loss} per share")
else:
    print("Breaking even!")

# Risk check example
risk_amount = account_balance * risk_per_trade

if risk_amount > 1000:
    print("⚠️ Warning: Risk amount is high!")
else:
    print("✓ Risk amount is within limits")

# ============================================
# EXERCISES FOR YOU TO TRY
# ============================================

print("\n" + "="*50)
print("🎯 YOUR TURN - COMPLETE THESE EXERCISES")
print("="*50)

print("""
Exercise 1: Create Your Variables
Create variables for:
- Your name
- Your favorite stock
- How much you'd invest
- Your target return percentage

Then print them all in a formatted message.
""")

# TODO: Write your code here
# Example:
# my_name = "..."
# favorite_stock = "..."



print("""
Exercise 2: Calculate Position Size
Given:
- Account size: $100,000
- Risk per trade: 1.5%
- Stock price: $250
- Stop loss: $240

Calculate:
- Maximum dollar risk
- Number of shares to buy
- Total position value

Print the results.
""")

# TODO: Write your code here
# Hints:
# dollar_risk = account_size * (risk_percentage / 100)
# risk_per_share = entry_price - stop_loss
# shares_to_buy = dollar_risk / risk_per_share



print("""
Exercise 3: Profit Calculator
Ask the user for:
- Number of shares bought
- Buy price
- Current price

Calculate and display the profit/loss.
""")

# TODO: Write your code here



# ============================================
# CONGRATULATIONS!
# ============================================

print("\n" + "="*50)
print("🎉 You've completed Module 1!")
print("="*50)
print("""
What you learned:
✓ How to run Python code
✓ Print statements
✓ Variables (strings, numbers, booleans)
✓ Math operations
✓ String manipulation
✓ User input
✓ If statements

Next Steps:
1. Complete the exercises above
2. Experiment - change values and see what happens!
3. Move to 02_data_structures.py when ready
4. Don't worry about mistakes - they're how you learn!

Remember: Every expert was once a beginner. Keep going! 💪
""")

# ============================================
# CHALLENGE (OPTIONAL)
# ============================================

print("""
🏆 CHALLENGE: Mini Trading Journal
Create a simple script that:
1. Asks for trade details (symbol, entry, exit, shares)
2. Calculates profit/loss
3. Calculates return percentage
4. Displays a summary

This combines everything you learned!
""")

# Challenge code space:




# ============================================
# DEBUGGING TIPS
# ============================================

"""
Common Beginner Mistakes:

1. Forgetting quotes around strings
   Wrong: print(Hello)
   Right: print("Hello")

2. Using = instead of == for comparison
   Wrong: if x = 5
   Right: if x == 5

3. Indentation errors (Python cares about spaces!)
   Wrong:
   if True:
   print("Hello")
   
   Right:
   if True:
       print("Hello")

4. Variable name typos
   Python is case-sensitive: "Name" ≠ "name"

5. Forgetting to convert input to numbers
   Wrong: x = input("Number: ")  # This is a string!
   Right: x = int(input("Number: "))

Always read error messages - they tell you what's wrong!
"""
