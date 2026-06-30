# AI Agent Learning Hub 🤖

Your personal workspace for learning and building AI agents with Python, LLMs, and automation.

## 📁 Project Structure

```
AI-Agent-Learning-Hub/
├── 01-Learning-Path/           # Progressive learning modules
│   ├── 01-Python-Basics/       # Python fundamentals
│   ├── 02-API-Integration/     # Working with APIs
│   ├── 03-Simple-Agents/       # Basic agent patterns
│   └── 04-Advanced-Agents/     # Complex multi-agent systems
│
├── 02-Production-Agents/       # Your real-world agents
│   ├── Email-Agent/            # Email categorization & summarization
│   ├── Schwab-Trading-Agent/   # Schwab API integration
│   └── Risk-Management-Agent/  # Position sizing & risk analysis
│
├── 03-Local-LLM/              # Local LLM integration
│   ├── LM-Studio-Integration/ # LM Studio connection setup
│   └── Model-Testing/         # Test different models
│
├── Agentic-Hub-Governance/       # Reusable components
│   ├── config/                # Configuration files
│   ├── utils/                 # Helper functions
│   └── api-credentials/       # API keys (NEVER commit!)
│
├── 05-Documentation/          # Your notes and guides
├── 06-Experiments/           # Testing ground
└── venv/                     # Python virtual environment
```

## 🚀 Quick Start

### 1. Set Up Python Environment
```bash
# Navigate to project folder
cd AI-Agent-Learning-Hub

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Your Learning Path

**Start here → 01-Learning-Path/01-Python-Basics/**

Follow the numbered folders in order. Each contains:
- README with instructions
- Example scripts
- Exercises

### 3. Connect LM Studio

Once you've completed basic modules:
- Start LM Studio
- Load a model (recommended: Mistral 7B or Llama 2 7B for beginners)
- See **03-Local-LLM/LM-Studio-Integration/** for connection code

## 🎯 Your Goals Roadmap

### Phase 1: Foundations (Weeks 1-2)
- [ ] Complete Python Basics
- [ ] Learn API basics with simple REST APIs
- [ ] Build your first simple chatbot

### Phase 2: Agent Basics (Weeks 3-4)
- [ ] Create a basic agent with LangChain
- [ ] Connect to LM Studio locally
- [ ] Build a simple email reader

### Phase 3: Production Agents (Weeks 5-8)
- [ ] Email categorization agent
- [ ] Schwab API connection (read-only first)
- [ ] Basic risk calculations

### Phase 4: Advanced (Weeks 9-12)
- [ ] Multi-agent systems
- [ ] Automated order submission
- [ ] Full position management system

## 📚 Essential Resources

- **Python for Beginners**: https://www.python.org/about/gettingstarted/
- **LangChain Documentation**: https://python.langchain.com/
- **LM Studio**: https://lmstudio.ai/docs
- **Schwab API**: https://developer.schwab.com/
- **OpenAI Cookbook**: https://cookbook.openai.com/

## ⚠️ Critical Safety Rules

1. **Never commit API keys** - Use .env files (already in .gitignore)
2. **Test with paper trading** - Never risk real money while learning
3. **Start small** - Get each module working before moving on
4. **Use version control** - Commit your progress regularly
5. **Backup your work** - Push to GitHub regularly

## 🆘 Getting Help

- Each folder has its own README with detailed instructions
- Check 05-Documentation/ for troubleshooting guides
- Use 06-Experiments/ to test ideas safely

## 📝 VS Code Setup

Recommended Extensions:
- Python (Microsoft)
- Pylance
- Python Debugger
- GitLens
- Code Spell Checker

To install: Open VS Code → Extensions (Ctrl+Shift+X) → Search and install each

---
**Current Status**: Environment Setup Phase  
**Last Updated**: 2025-12-31  
**Python Level**: Beginner  
**Next Step**: Complete 01-Learning-Path/01-Python-Basics/
