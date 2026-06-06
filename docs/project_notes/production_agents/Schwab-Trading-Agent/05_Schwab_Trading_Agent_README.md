# Schwab Trading Agent 📈

**Status**: Advanced Template / Work in Progress  
**Difficulty**: Advanced  
**Prerequisites**: Complete ALL previous modules + Email Agent

## ⚠️ CRITICAL WARNING

**TRADING WITH REAL MONEY INVOLVES SIGNIFICANT RISK**

Before proceeding:
1. ✅ Complete ALL learning modules
2. ✅ Test EXTENSIVELY with paper trading
3. ✅ Understand position sizing and risk management
4. ✅ Have emergency stop mechanisms
5. ✅ Start with TINY positions
6. ✅ Never risk more than you can afford to lose

**This is NOT financial advice. You are responsible for your trades.**

## 🎯 Project Goals

Build an AI agent that:
1. **Phase 1**: Read-only account access (balances, positions)
2. **Phase 2**: Risk calculations and position sizing
3. **Phase 3**: Order generation (review before submission)
4. **Phase 4**: Automated order submission (with safeguards)

## 📋 Prerequisites

### Technical Requirements
- Python 3.9+
- Completed Python Basics, API Integration, Simple Agents
- Working LM Studio setup
- Understanding of async programming

### Trading Knowledge Required
- Position sizing concepts
- Risk management principles
- Order types (market, limit, stop)
- Basic technical analysis
- **ThinkScript experience** (you have this! ✓)

### Account Requirements
- Schwab brokerage account
- API access approved (may take days/weeks)
- Paper trading account for testing

## 🔐 Security Checklist

Before writing ANY code:

- [ ] Read Schwab API Terms of Service
- [ ] Understand rate limits
- [ ] Set up 2-factor authentication
- [ ] Use environment variables for ALL credentials
- [ ] Implement order size limits
- [ ] Add confirmation steps for orders
- [ ] Create emergency stop mechanism
- [ ] Set daily loss limits
- [ ] Test EVERYTHING in paper trading first

## 📚 Schwab API Documentation

**Official Resources:**
- Developer Portal: https://developer.schwab.com/
- API Documentation: https://developer.schwab.com/products/trader-api--individual
- Python Examples: Check GitHub for community libraries

**Key Endpoints You'll Use:**
1. Account Information
2. Account Balances
3. Positions
4. Orders (read and place)
5. Market Data (if approved)

## 🏗️ Project Structure

```
Schwab-Trading-Agent/
├── README.md                    # This file
├── .env.example                # Template
├── .env                        # Credentials (NOT in git!)
│
├── 01-authentication/
│   ├── auth_setup.py           # OAuth2 setup
│   ├── token_manager.py        # Refresh tokens
│   └── README.md               # Auth guide
│
├── 02-read-only/
│   ├── account_info.py         # Get balances
│   ├── position_reader.py      # Read positions
│   ├── order_history.py        # View past orders
│   └── README.md
│
├── 03-risk-management/
│   ├── position_sizer.py       # Calculate position sizes
│   ├── risk_calculator.py      # Risk per trade
│   ├── portfolio_analyzer.py   # Overall risk
│   └── README.md
│
├── 04-order-generation/
│   ├── order_builder.py        # Create order objects
│   ├── order_validator.py      # Validate before sending
│   ├── order_preview.py        # Review orders
│   └── README.md
│
├── 05-automation/
│   ├── trading_agent.py        # Main agent
│   ├── strategy_executor.py    # Execute strategies
│   ├── monitoring.py           # Track performance
│   └── README.md
│
├── config/
│   ├── trading_config.py       # Risk parameters
│   ├── strategy_config.py      # Strategy settings
│   └── safety_limits.py        # Hard limits
│
├── utils/
│   ├── api_client.py           # Schwab API wrapper
│   ├── data_processor.py       # Process responses
│   └── logger.py               # Trade logging
│
├── strategies/
│   ├── base_strategy.py        # Abstract base
│   └── example_strategy.py     # Template
│
├── tests/
│   ├── test_api.py
│   ├── test_risk.py
│   └── test_orders.py
│
└── logs/
    ├── trades/                 # Trade log files
    ├── errors/                 # Error logs
    └── performance/            # Performance metrics
```

## 🚀 Development Phases

### Phase 1: Authentication & Read-Only (Weeks 1-2)

**Goal**: Connect to Schwab API safely

**Tasks**:
1. Register for API access
2. Implement OAuth2 authentication
3. Store and refresh tokens securely
4. Test connection
5. Read account balances
6. Read current positions
7. View order history

**Success Criteria**:
- [ ] Can authenticate successfully
- [ ] Tokens refresh automatically
- [ ] Can retrieve account balance
- [ ] Can list all positions
- [ ] Error handling works

**Safety**: Read-only, no risk

---

### Phase 2: Risk Management (Weeks 3-4)

**Goal**: Calculate safe position sizes

**Implement**:

```python
class RiskManager:
    """
    Calculate position sizes based on account and risk parameters
    """
    def __init__(self, account_balance, risk_per_trade=0.01):
        self.account_balance = account_balance
        self.risk_per_trade = risk_per_trade  # 1% default
        
    def calculate_position_size(self, entry_price, stop_loss):
        """
        Calculate shares to buy based on risk
        
        Example:
        Account: $50,000
        Risk: 1% = $500
        Entry: $100
        Stop: $95
        Risk per share: $5
        Shares: $500 / $5 = 100 shares
        """
        dollar_risk = self.account_balance * self.risk_per_trade
        risk_per_share = abs(entry_price - stop_loss)
        
        if risk_per_share == 0:
            return 0
            
        shares = dollar_risk / risk_per_share
        
        # Round down to avoid over-risking
        return int(shares)
    
    def validate_position(self, symbol, shares, price):
        """
        Check if position is within limits
        """
        position_value = shares * price
        max_position = self.account_balance * 0.20  # Max 20% per position
        
        if position_value > max_position:
            return False, f"Position too large: ${position_value:.2f}"
        
        return True, "Position valid"
```

**Tasks**:
- [ ] Implement position sizing
- [ ] Add portfolio risk calculation
- [ ] Create risk validation
- [ ] Test with various scenarios
- [ ] Add maximum position size limits

**Integration with ThinkScript**:
- Export signals from ThinkScript
- Import into Python
- Calculate position sizes
- Generate order recommendations

---

### Phase 3: Order Generation (Weeks 5-6)

**Goal**: Create orders (don't submit yet!)

**Features**:
1. Build order objects
2. Validate parameters
3. Preview orders
4. Save for manual submission
5. Generate human-readable reports

**Example Order Builder**:

```python
class OrderBuilder:
    """
    Build Schwab-compatible order objects
    """
    def create_order(self, symbol, quantity, order_type='LIMIT', 
                     price=None, stop_price=None):
        """
        Create an order object
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            quantity: Number of shares
            order_type: 'MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT'
            price: Limit price (required for LIMIT orders)
            stop_price: Stop price (required for STOP orders)
        """
        order = {
            "orderType": order_type,
            "session": "NORMAL",
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": "BUY",
                    "quantity": quantity,
                    "instrument": {
                        "symbol": symbol,
                        "assetType": "EQUITY"
                    }
                }
            ]
        }
        
        if order_type == "LIMIT" and price:
            order["price"] = price
        
        if order_type in ["STOP", "STOP_LIMIT"] and stop_price:
            order["stopPrice"] = stop_price
            
        return order
    
    def preview_order(self, order):
        """
        Create human-readable preview
        """
        leg = order['orderLegCollection'][0]
        
        preview = f"""
        ORDER PREVIEW
        ═══════════════════════════════════════
        Symbol:     {leg['instrument']['symbol']}
        Action:     {leg['instruction']}
        Quantity:   {leg['quantity']} shares
        Type:       {order['orderType']}
        """
        
        if 'price' in order:
            preview += f"Price:      ${order['price']:.2f}\n"
        if 'stopPrice' in order:
            preview += f"Stop Price: ${order['stopPrice']:.2f}\n"
            
        preview += "═══════════════════════════════════════"
        
        return preview
```

**Tasks**:
- [ ] Create order templates
- [ ] Add validation logic
- [ ] Implement preview function
- [ ] Test with paper account
- [ ] Create order logs

**Safety**: Still not submitting real orders!

---

### Phase 4: AI-Powered Analysis (Weeks 7-8)

**Goal**: Use LM Studio for trade analysis

**Use Cases**:

1. **Pre-Trade Analysis**:
```python
def analyze_trade_with_ai(symbol, entry, stop, target):
    prompt = f"""
    Analyze this trade setup:
    
    Symbol: {symbol}
    Entry: ${entry}
    Stop Loss: ${stop}
    Target: ${target}
    
    Risk/Reward: {(target-entry)/(entry-stop):.2f}
    
    Evaluate:
    1. Is the R/R ratio acceptable?
    2. What could go wrong?
    3. Any concerns?
    
    Be concise and objective.
    """
    
    return call_lm_studio(prompt)
```

2. **Portfolio Review**:
```python
def daily_portfolio_review(positions, performance):
    prompt = f"""
    Review my portfolio:
    
    Positions: {positions}
    Today's P/L: {performance}
    
    Identify:
    1. Largest risks
    2. Concentration issues
    3. Recommendations
    """
    
    return call_lm_studio(prompt)
```

3. **Risk Warnings**:
```python
def check_risk_exposure(portfolio_data):
    prompt = f"""
    You are a risk manager. Analyze:
    {portfolio_data}
    
    Flag any concerning patterns or excessive risk.
    """
    
    return call_lm_studio(prompt)
```

---

### Phase 5: Automated Trading (Weeks 9-12)

**⚠️ EXTREME CAUTION REQUIRED**

Only proceed if:
- ✅ All previous phases work perfectly
- ✅ Tested for weeks in paper trading
- ✅ Understand every line of code
- ✅ Have kill switches implemented
- ✅ Starting with tiny positions

**Required Safeguards**:

```python
class TradingSafeguards:
    """
    Safety limits for automated trading
    """
    def __init__(self):
        self.MAX_DAILY_LOSS = 500  # Stop trading if hit
        self.MAX_POSITION_SIZE = 1000  # Dollars, not shares
        self.MAX_TRADES_PER_DAY = 5
        self.ALLOWED_HOURS = (9, 30, 16, 0)  # 9:30 AM - 4:00 PM EST
        
        self.trades_today = 0
        self.pnl_today = 0
        self.circuit_breaker_triggered = False
        
    def can_trade(self):
        """
        Check if trading is allowed
        """
        # Check daily loss limit
        if self.pnl_today <= -self.MAX_DAILY_LOSS:
            self.circuit_breaker_triggered = True
            return False, "Daily loss limit reached"
        
        # Check trade count
        if self.trades_today >= self.MAX_TRADES_PER_DAY:
            return False, "Max trades reached"
        
        # Check time
        if not self._is_market_hours():
            return False, "Outside market hours"
        
        # Check circuit breaker
        if self.circuit_breaker_triggered:
            return False, "Circuit breaker active"
            
        return True, "OK to trade"
    
    def validate_order(self, order, account_balance):
        """
        Final validation before submission
        """
        # Calculate order value
        shares = order['orderLegCollection'][0]['quantity']
        # Get current price (from market data API)
        price = self._get_current_price(
            order['orderLegCollection'][0]['instrument']['symbol']
        )
        
        order_value = shares * price
        
        # Check against max position size
        if order_value > self.MAX_POSITION_SIZE:
            return False, f"Order value ${order_value:.2f} exceeds limit"
        
        # Check percentage of account
        if order_value > account_balance * 0.10:  # Max 10% per order
            return False, "Order exceeds 10% of account"
            
        return True, "Order validated"
```

**Additional Safety Features**:
1. Email alerts before every order
2. SMS notifications
3. Manual confirmation required
4. Automatic position closing at EOD
5. Emergency stop button/file

---

## 🔧 Configuration Example

**config/trading_config.py**:

```python
class TradingConfig:
    """
    Central configuration for trading agent
    """
    # Account
    ACCOUNT_ID = os.getenv('SCHWAB_ACCOUNT_ID')
    
    # Risk Management
    DEFAULT_RISK_PER_TRADE = 0.01  # 1%
    MAX_RISK_PER_TRADE = 0.02      # 2% hard limit
    MAX_PORTFOLIO_RISK = 0.06      # 6% total
    MAX_POSITION_SIZE = 0.20       # 20% of account max
    
    # Order Limits
    MAX_TRADES_PER_DAY = 5
    MAX_ORDER_VALUE = 1000         # $1000 per order max
    MIN_ORDER_VALUE = 100          # Minimum $100
    
    # Time Restrictions
    TRADING_START = (9, 30)        # 9:30 AM EST
    TRADING_END = (15, 45)         # 3:45 PM EST (before close)
    
    # Stop Loss
    REQUIRE_STOP_LOSS = True       # Must have stop on every trade
    MAX_STOP_DISTANCE = 0.10       # Max 10% from entry
    
    # Emergency Contacts
    ALERT_EMAIL = os.getenv('ALERT_EMAIL')
    ALERT_PHONE = os.getenv('ALERT_PHONE')
    
    # Logging
    LOG_ALL_ORDERS = True
    LOG_ALL_API_CALLS = True
    
    # Paper Trading
    PAPER_TRADING_MODE = True      # START WITH THIS!
```

## 📊 Integration with ThinkScript

You mentioned you code in ThinkScript - here's how to integrate:

### Strategy 1: Export Signals
```thinkscript
# In ThinkOrSwim:
# Create study that plots buy/sell signals
# Export to file
# Python reads file and executes
```

### Strategy 2: API Calls
```python
# Read TOS signals via file watching
import watchdog

def on_signal_file_updated(signal_file):
    # Read signal
    # Validate
    # Calculate position size
    # Generate order
    # Submit (with all safeguards!)
```

### Strategy 3: Indicator Replication
```python
# Recreate your ThinkScript indicators in Python
# Use pandas for data manipulation
# Generate signals programmatically
```

## 📈 Example Risk Management Workflow

```python
# Complete workflow from signal to order:

1. Receive signal (from ThinkScript or other source)
   ↓
2. Get current account balance
   ↓
3. Calculate position size based on:
   - Account balance
   - Risk per trade (1%)
   - Stop loss distance
   ↓
4. Validate position:
   - Within daily trade limit?
   - Within position size limit?
   - Within portfolio risk limit?
   ↓
5. Build order object
   ↓
6. Get AI analysis (optional)
   ↓
7. Preview order
   ↓
8. Log order details
   ↓
9. Send email/SMS for confirmation
   ↓
10. Submit order (if automated)
    ↓
11. Monitor fill
    ↓
12. Set stop loss (if not bracket order)
    ↓
13. Log trade in journal
    ↓
14. Update daily P/L
```

## ✅ Launch Checklist

Before going live with ANY real money:

**Testing**:
- [ ] All functions tested individually
- [ ] Integration tests passed
- [ ] Ran in paper trading for minimum 1 month
- [ ] Win rate and P/L acceptable
- [ ] Error handling works perfectly
- [ ] Safeguards tested (including circuit breakers)

**Documentation**:
- [ ] All code commented
- [ ] Trade journal system in place
- [ ] Performance tracking ready
- [ ] Backup strategy documented

**Risk Management**:
- [ ] Position sizing validated
- [ ] Daily loss limits set
- [ ] Maximum position sizes set
- [ ] Emergency stop mechanism tested
- [ ] All alerts working (email, SMS)

**Legal/Compliance**:
- [ ] Read Schwab API terms
- [ ] Understand tax implications
- [ ] Have adequate records
- [ ] Emergency contact set

**Psychological**:
- [ ] Comfortable with risk
- [ ] Won't panic if system has issues
- [ ] Can afford to lose test capital
- [ ] Have realistic expectations

## 🆘 Emergency Procedures

### If Something Goes Wrong:

1. **Immediate Actions**:
   ```python
   # Create emergency_stop.txt file
   # Agent checks for this file every loop
   # If exists: Stop all trading, close positions, alert you
   ```

2. **Kill Switch**:
   - Keep emergency_stop.py ready to run
   - Closes all positions immediately
   - Disables agent

3. **Manual Override**:
   - Always have access to Schwab directly
   - Can manually close positions
   - Can cancel orders

4. **Contact Information**:
   - Schwab support number saved
   - Your emergency contact notified
   - Trading journal backed up

## 📚 Required Reading

Before implementing:

1. **Position Sizing**:
   - "Trade Your Way to Financial Freedom" - Van Tharp
   - "The Mathematics of Money Management" - Vince

2. **Risk Management**:
   - "Market Wizards" - Schwager (interviews with traders)
   - "Way of the Turtle" - Curtis Faith

3. **Python Trading**:
   - "Algorithmic Trading" - Chan
   - "Python for Finance" - Hilpisch

4. **API Documentation**:
   - Schwab API docs (read completely!)
   - OAuth2 best practices
   - Rate limiting strategies

## 🎯 Success Metrics

Track these to measure performance:

1. **Technical**:
   - API uptime
   - Order execution success rate
   - System error rate

2. **Trading**:
   - Win rate
   - Average win/loss
   - Max drawdown
   - Sharpe ratio

3. **Risk**:
   - Largest loss (should never exceed limits)
   - Number of circuit breaker triggers
   - Risk-adjusted returns

## 🔮 Future Enhancements

Once basic system is stable:

1. Multiple strategies running
2. Portfolio optimization
3. ML-based signal generation
4. Advanced order types
5. Options trading (very advanced)
6. Multi-broker support

---

## Final Reminder

**THIS IS REAL MONEY**

- Start with paper trading
- Test for MONTHS before going live
- Start with TINY positions
- Scale up slowly
- Have stop losses always
- Never risk more than 1-2% per trade
- Be prepared for losses
- Keep learning

**The code is the easy part. The hard part is discipline.**

---

**Ready to start?** Begin with Phase 1: Authentication & Read-Only Access.

Do NOT proceed to automated trading until you're completely confident.

**Questions?** Review all documentation. Test thoroughly. Be safe.
