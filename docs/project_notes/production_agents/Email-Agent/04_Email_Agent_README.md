# Email Categorization & Summarization Agent 📧

**Status**: Template / Work in Progress  
**Difficulty**: Intermediate  
**Prerequisites**: Complete Python Basics + API Integration + LM Studio setup

## 🎯 Project Goal

Build an AI agent that:
1. Connects to your email account
2. Reads emails from specified folders/labels
3. Categorizes them (Urgent, Important, Informational, Spam, etc.)
4. Generates daily summaries
5. Optionally: Auto-files emails into folders

## 🔐 Security First!

**CRITICAL SAFETY RULES:**

1. **Use App-Specific Passwords** (not your main password!)
   - Gmail: https://myaccount.google.com/apppasswords
   - Outlook: https://account.microsoft.com/security
   
2. **Never commit credentials to Git**
   - Store in `.env` file (already in .gitignore)
   - Never share your `.env` file
   
3. **Start with Read-Only**
   - Test with IMAP (read-only) first
   - Only enable write access when confident
   
4. **Test on a Separate Email First**
   - Create a test Gmail/Outlook account
   - Forward some emails there
   - Don't risk your main account while learning!

## 📋 Required Setup

### 1. Email Account Configuration

**For Gmail:**
```
1. Enable IMAP in Gmail Settings → Forwarding and POP/IMAP
2. Create App Password (with 2FA enabled)
3. Note: imap.gmail.com, port 993
```

**For Outlook/Hotmail:**
```
1. Enable IMAP in Settings
2. Use your account password (or app password if 2FA)
3. Note: outlook.office365.com, port 993
```

### 2. Install Required Packages

```bash
pip install python-dotenv imap-tools beautifulsoup4 lxml
```

### 3. Create .env File

```bash
# Copy template
cp .env.example .env

# Edit .env (add your credentials):
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_app_specific_password
EMAIL_SERVER=imap.gmail.com
EMAIL_PORT=993

# LM Studio settings
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
```

## 📁 Project Structure

```
Email-Agent/
├── README.md                    # This file
├── .env.example                # Template for credentials
├── .env                        # Your actual credentials (NOT in git!)
├── email_reader.py             # Read emails
├── email_categorizer.py        # Categorize with AI
├── email_summarizer.py         # Generate summaries
├── main.py                     # Orchestrates everything
├── config.py                   # Configuration settings
├── utils/
│   ├── email_utils.py          # Helper functions
│   └── llm_utils.py            # LM Studio interaction
├── data/
│   ├── categories.json         # Your category definitions
│   └── summaries/              # Daily summary outputs
└── tests/
    └── test_connection.py      # Test email connection
```

## 🚀 Development Phases

### Phase 1: Basic Email Reading (Start Here!)

**Goal**: Connect and read emails

**File**: `email_reader.py`

```python
# Pseudocode structure:
1. Load credentials from .env
2. Connect to IMAP server
3. Select inbox
4. Fetch recent emails (last 24 hours)
5. Extract: sender, subject, date, body
6. Print to console
```

**Test**: Can you read your last 10 emails?

---

### Phase 2: LM Studio Integration

**Goal**: Use local LLM to analyze emails

**File**: `email_categorizer.py`

```python
# Pseudocode:
1. Take email content
2. Create prompt for LLM:
   "Categorize this email into one of:
    - Urgent: Needs immediate action
    - Important: Read today
    - Informational: Read when time
    - Spam: Unwanted
    
    Email: [email content]
    Category:"
3. Send to LM Studio
4. Parse response
5. Return category
```

**Test**: Categorize 5 test emails manually, check accuracy

---

### Phase 3: Summarization

**Goal**: Generate daily summaries

**File**: `email_summarizer.py`

```python
# Pseudocode:
1. Group emails by category
2. For each category:
   - Count emails
   - Extract key subjects
   - Generate summary with LLM
3. Create formatted report
4. Save to file or email to yourself
```

**Test**: Generate summary for today's emails

---

### Phase 4: Automation

**Goal**: Run automatically every morning

**Options**:
- Windows Task Scheduler
- Python `schedule` library
- Cron job (Mac/Linux)

**Caution**: Test thoroughly before automating!

---

## 🔍 Example Categorization Prompt

```python
CATEGORIZATION_PROMPT = """
You are an email categorization assistant.

Analyze this email and categorize it into ONE of these categories:

1. URGENT - Requires immediate action today
   Examples: Deadlines, urgent requests, account alerts

2. IMPORTANT - Should be read today but not urgent
   Examples: Work emails, important updates, invitations

3. INFORMATIONAL - Can be read later
   Examples: Newsletters, notifications, updates

4. SPAM - Unwanted or promotional
   Examples: Marketing, junk, unsolicited

5. FINANCIAL - Related to money, trading, accounts
   Examples: Broker alerts, bank notifications, trade confirmations

Email Details:
From: {sender}
Subject: {subject}
Body: {body}

Respond with ONLY the category name (URGENT, IMPORTANT, INFORMATIONAL, SPAM, or FINANCIAL).
Do not include any explanation.
"""
```

## 📊 Daily Summary Template

```
====================================
Daily Email Summary
Date: {date}
Total Emails: {total_count}
====================================

🚨 URGENT ({urgent_count}):
- {urgent_email_1_subject}
- {urgent_email_2_subject}

⭐ IMPORTANT ({important_count}):
- {important_email_1_subject}
- {important_email_2_subject}

📰 INFORMATIONAL ({info_count}):
- Top 3 newsletters received
- Notable updates

💰 FINANCIAL ({financial_count}):
- Trading alerts
- Account notifications

🗑️ SPAM ({spam_count}):
- Auto-archived

====================================
Action Items:
1. {action_1}
2. {action_2}
====================================
```

## ⚙️ Configuration Options

**config.py example:**

```python
# Email settings
CHECK_INTERVAL_HOURS = 24
MAX_EMAILS_PER_CHECK = 100
EMAIL_AGE_DAYS = 1

# Categories
CATEGORIES = [
    "URGENT",
    "IMPORTANT", 
    "INFORMATIONAL",
    "SPAM",
    "FINANCIAL"
]

# LLM settings
TEMPERATURE = 0.3  # Lower for consistent categorization
MAX_TOKENS = 100
```

## 🧪 Testing Strategy

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test email reading
3. **End-to-End Tests**: Full workflow with test emails
4. **Manual Review**: Check categorizations for accuracy

**Create test emails covering**:
- Different senders
- Various subjects
- Short and long bodies
- HTML emails
- Plain text emails

## 🎯 Success Metrics

Track these to measure your agent's performance:

- **Accuracy**: % correctly categorized (compare to manual)
- **Speed**: Time to process 100 emails
- **Reliability**: Runs without errors
- **Usefulness**: Does it save you time?

**Goal**: >90% accuracy, <5 min for 100 emails

## 🚧 Common Challenges

1. **HTML Email Parsing**
   - Solution: Use BeautifulSoup to extract text
   - Remove formatting, keep content

2. **Long Emails**
   - Solution: Truncate to first 500 words
   - LLM context limits

3. **Inconsistent Categories**
   - Solution: Lower temperature (0.2-0.3)
   - More specific prompts

4. **False Spam Detection**
   - Solution: Whitelist important senders
   - Two-pass system: quick filter, then detailed

## 📚 Learning Resources

- [IMAP Protocol](https://tools.ietf.org/html/rfc3501)
- [imap-tools Docs](https://github.com/ikvk/imap_tools)
- [Email Parsing Guide](https://realpython.com/python-send-email/)
- [Prompt Engineering](https://www.promptingguide.ai/)

## ✅ Milestones

Progress tracking:

- [ ] Successfully connect to email server
- [ ] Read and parse 10 test emails
- [ ] Categorize emails with LM Studio
- [ ] Generate daily summary
- [ ] Save summaries to files
- [ ] Achieve >90% categorization accuracy
- [ ] Automate daily runs
- [ ] Handle errors gracefully

## 🔮 Future Enhancements

Once basic version works:

1. **Priority Scoring**: Rank emails within categories
2. **Sender Analysis**: Learn sender importance over time
3. **Thread Detection**: Group related emails
4. **Smart Filtering**: Auto-archive based on rules
5. **Sentiment Analysis**: Detect urgent tone
6. **Attachment Handling**: Categorize by attachment type
7. **Multi-Account**: Handle multiple email accounts

## ⚠️ Important Reminders

- **Privacy**: Your emails contain sensitive data
- **Local Processing**: That's why we use LM Studio (stays on your computer)
- **Backups**: Never delete emails automatically at first
- **Testing**: Use test account until perfect
- **Credentials**: NEVER commit .env file!

## 🆘 Troubleshooting

**Can't connect to email**:
- Check IMAP is enabled
- Verify app password
- Try telnet to test connection

**LM Studio not responding**:
- Is server running?
- Is model loaded?
- Check test_lm_studio_connection.py

**Categorization inaccurate**:
- Refine prompt
- Lower temperature
- Try different model
- Add more examples to prompt

---

**Ready to start?** Begin with Phase 1: Basic Email Reading!

Create `email_reader.py` and test connecting to your email.
