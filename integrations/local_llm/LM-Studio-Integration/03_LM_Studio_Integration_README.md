# LM Studio Integration Guide 🤖

Connect your Python scripts to local LLMs running in LM Studio

## 🎯 What You'll Learn

- How to start LM Studio and load models
- Connect Python to LM Studio's API
- Send prompts and get responses
- Build your first local AI agent
- Compare different models

## 📋 Prerequisites

Before starting this module:
- ✅ Complete Python Basics (01-Learning-Path/01-Python-Basics)
- ✅ Install LM Studio from https://lmstudio.ai
- ✅ Download at least one model in LM Studio

## 🚀 Quick Start Guide

### Step 1: Set Up LM Studio

1. **Open LM Studio**
   - Launch the LM Studio application

2. **Download a Model** (if you haven't already)
   - Recommended for beginners:
     * `TheBloke/Mistral-7B-Instruct-v0.2-GGUF` (Good balance)
     * `TheBloke/Llama-2-7B-Chat-GGUF` (Popular, reliable)
     * `TheBloke/Phi-2-GGUF` (Smaller, faster)
   
   - Click "Search" tab
   - Search for the model name
   - Download the `Q4_K_M` version (good quality, reasonable size)

3. **Load the Model**
   - Go to "Chat" tab
   - Select your downloaded model from dropdown
   - Click "Load Model"
   - Wait for it to load (may take 30-60 seconds)

4. **Start the Local Server**
   - Click "Local Server" tab
   - Click "Start Server"
   - Note the URL (usually `http://localhost:1234`)
   - Keep LM Studio running while testing your code!

### Step 2: Test Connection with Python

```bash
# In your terminal (with venv activated):
cd AI-Agent-Learning-Hub/03-Local-LLM/LM-Studio-Integration

# Run the test script
python test_connection.py
```

## 📁 Files in This Folder

```
LM-Studio-Integration/
├── README.md                    # This file
├── test_connection.py          # Simple connection test
├── basic_chat.py               # Interactive chat
├── financial_agent.py          # Example: Stock analysis agent
├── .env.example                # Template for API settings
└── lm_studio_utils.py          # Reusable helper functions
```

## 🔧 Configuration

### Create Your .env File

Copy the example and customize:

```bash
# Copy the template
copy .env.example .env

# Edit .env with your settings:
# LM_STUDIO_URL=http://localhost:1234
# DEFAULT_MODEL=mistral-7b-instruct-v0.2
# MAX_TOKENS=2000
# TEMPERATURE=0.7
```

Never commit the .env file to Git (it's in .gitignore)!

## 📝 Example Code Snippets

### Basic Connection
```python
import requests
import json

def call_lm_studio(prompt, url="http://localhost:1234/v1/chat/completions"):
    """
    Send a prompt to LM Studio and get response
    """
    headers = {"Content-Type": "application/json"}
    
    data = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    return result['choices'][0]['message']['content']

# Test it
response = call_lm_studio("What is Python?")
print(response)
```

### Financial Analysis Agent
```python
def analyze_stock(symbol, model_url="http://localhost:1234/v1/chat/completions"):
    """
    Ask LM Studio to analyze a stock
    """
    prompt = f"""
    You are a financial analysis assistant.
    Provide a brief analysis of {symbol} stock including:
    - What the company does
    - Industry sector
    - Key considerations for investors
    
    Keep it concise (3-4 sentences).
    """
    
    return call_lm_studio(prompt, model_url)

# Use it
analysis = analyze_stock("AAPL")
print(analysis)
```

## 🎯 Practice Projects

### Project 1: Stock Screener Agent (Beginner)
Create an agent that:
- Takes a list of stock symbols
- Asks LM Studio about each one
- Summarizes industries and sectors
- Saves results to a file

**Estimated time**: 1-2 hours

### Project 2: Email Categorizer (Intermediate)
Build an agent that:
- Reads sample emails from a file
- Uses LM Studio to categorize them
- Sorts into folders: urgent, informational, spam
- Generates a summary

**Estimated time**: 2-3 hours

### Project 3: Trading Journal Analyzer (Advanced)
Create an agent that:
- Reads your trading journal entries
- Identifies patterns in wins/losses
- Suggests improvements
- Tracks emotional trading indicators

**Estimated time**: 4-6 hours

## ⚙️ Model Parameters Explained

**Temperature** (0.0 - 1.0):
- 0.0 = Deterministic, consistent answers
- 0.7 = Balanced creativity and consistency (recommended)
- 1.0 = More creative, varied responses

Use lower temperature (0.1-0.3) for:
- Data extraction
- Classification tasks
- Factual analysis

Use higher temperature (0.7-0.9) for:
- Creative writing
- Brainstorming
- Varied responses

**Max Tokens**:
- Controls response length
- 1 token ≈ 0.75 words
- 500 tokens ≈ 375 words
- Set based on your needs

**Top P** (0.0 - 1.0):
- Alternative to temperature
- 0.9 = Use top 90% probable words
- Lower = more focused responses

## 🔍 Troubleshooting

### "Connection refused" error
- ✓ Is LM Studio running?
- ✓ Is the local server started?
- ✓ Check the port (default: 1234)
- ✓ Try: `http://127.0.0.1:1234` instead of `localhost`

### "Model not loaded" error
- ✓ Load a model in LM Studio first
- ✓ Wait for loading to complete
- ✓ Check LM Studio console for errors

### Slow responses
- ✓ Use a smaller model (7B instead of 13B)
- ✓ Reduce max_tokens
- ✓ Close other applications
- ✓ Check GPU/CPU usage

### Gibberish responses
- ✓ Model might not be fully loaded
- ✓ Try restarting LM Studio
- ✓ Use a different quantization (Q4 or Q5)

## 📊 Comparing Models

Create a test script to compare different models:

```python
models = ["mistral-7b", "llama-2-7b", "phi-2"]
prompt = "Explain the Sharpe ratio in one sentence."

for model in models:
    # Load model in LM Studio
    # Run prompt
    # Compare responses
```

Track:
- Response quality
- Speed
- Token usage
- Accuracy

## 🔐 Best Practices

1. **Always validate responses**
   - LLMs can hallucinate (make up facts)
   - Critical for financial data!
   - Cross-reference important information

2. **Handle errors gracefully**
   ```python
   try:
       response = call_lm_studio(prompt)
   except Exception as e:
       print(f"Error: {e}")
       response = "Unable to get response"
   ```

3. **Don't send sensitive data**
   - Even though it's local, be careful
   - Don't log API keys or passwords
   - Review prompts before sending

4. **Monitor resource usage**
   - Large models use lots of RAM
   - Close when not in use
   - Consider using smaller models for testing

## 📚 Additional Resources

- [LM Studio Documentation](https://lmstudio.ai/docs)
- [GGUF Model Format](https://github.com/ggerganov/llama.cpp)
- [Hugging Face Model Hub](https://huggingface.co/models)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

## ✅ Completion Checklist

You're ready for the next phase when you can:

- [ ] Start and configure LM Studio
- [ ] Load and run a model locally
- [ ] Connect Python to LM Studio
- [ ] Send prompts and get responses
- [ ] Handle errors properly
- [ ] Understand model parameters
- [ ] Build a simple agent that uses local LLM

## 🎯 Next Steps

Once comfortable with LM Studio:
1. Combine with API skills (Phase 2)
2. Build your email categorization agent
3. Create the Schwab integration agent
4. Experiment with different models
5. Build multi-agent systems

---

**Remember**: Local LLMs give you privacy and control. Start small, experiment, and gradually build more complex agents!

**Need Help?**: Check `05-Documentation/troubleshooting.md` or the LM Studio Discord community.
