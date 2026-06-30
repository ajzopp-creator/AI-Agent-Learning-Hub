# Complete Setup Guide 🚀

**For Complete Beginners to Python and VS Code**

Follow this guide step-by-step to get your development environment ready.

## ⏱️ Estimated Time

Total setup time: 1-2 hours

---

## 📋 Prerequisites

Before you begin, make sure you have:
- [ ] Windows computer (you have this ✓)
- [ ] Administrator access
- [ ] Internet connection
- [ ] At least 5GB free disk space

---

## Step 1: Install Python (15 minutes)

### 1.1 Download Python

1. Go to https://www.python.org/downloads/
2. Click the big yellow "Download Python 3.x.x" button
3. Save the installer file

### 1.2 Install Python

1. **Double-click** the installer
2. ⚠️ **CRITICAL**: Check the box "Add Python to PATH" (at bottom)
3. Click "Install Now"
4. Wait for installation to complete
5. Click "Close"

### 1.3 Verify Installation

1. Press `Windows Key + R`
2. Type: `cmd`
3. Press Enter (opens Command Prompt)
4. Type: `python --version`
5. Press Enter

**You should see**: `Python 3.11.x` (or similar)

**If you see an error**:
- Python wasn't added to PATH
- Uninstall and reinstall, checking the PATH box

---

## Step 2: Set Up Visual Studio Code (20 minutes)

### 2.1 Install VS Code

1. Go to https://code.visualstudio.com/
2. Click "Download for Windows"
3. Run the installer
4. Accept defaults
5. **Check** "Add to PATH"
6. Click Install

### 2.2 First Launch

1. Open VS Code (from Start menu or desktop)
2. You'll see a welcome screen
3. Close any tutorial tabs for now

### 2.3 Install Python Extension

This makes VS Code understand Python:

1. Click Extensions icon (left sidebar, looks like 4 squares)
   - Or press `Ctrl+Shift+X`
2. Search: `Python`
3. Click the **Microsoft** Python extension (has millions of downloads)
4. Click "Install"
5. Wait for installation

### 2.4 Install Recommended Extensions

Install these for the best experience:

**Essential**:
- Python (Microsoft) ✓ Already installed
- Pylance (Microsoft) - Auto-completes Python code
- Python Debugger (Microsoft) - Helps find bugs

**Helpful**:
- GitLens - See code history
- indent-rainbow - Makes indentation visible
- Code Spell Checker - Catches typos
- Material Icon Theme - Better file icons

**How to install**:
1. Click Extensions (Ctrl+Shift+X)
2. Search for extension name
3. Click Install
4. Repeat for each

### 2.5 Configure Settings

1. Press `Ctrl+,` (opens settings)
2. Search: `python formatting provider`
3. Select: `black`
4. Search: `auto save`
5. Set to: `afterDelay`

This auto-saves your files!

---

## Step 3: Set Up Your Project Folder (10 minutes)

### 3.1 Locate Your Project

The PowerShell commands earlier created:
`C:\Users\Trader\AI-Agent-Learning-Hub`

### 3.2 Open in VS Code

**Method 1 - From VS Code**:
1. Click File → Open Folder
2. Navigate to `C:\Users\Trader\`
3. Select `AI-Agent-Learning-Hub`
4. Click "Select Folder"
5. If asked "Do you trust the authors?", click "Yes, I trust"

**Method 2 - From Explorer**:
1. Open File Explorer
2. Navigate to `C:\Users\Trader\AI-Agent-Learning-Hub`
3. Right-click inside the folder
4. Select "Open with Code"

### 3.3 Explore the Folder

In VS Code's left sidebar (Explorer), you'll see:
```
AI-Agent-Learning-Hub/
├── 01-Learning-Path/
├── 02-Production-Agents/
├── 03-Local-LLM/
├── Agentic-Hub-Governance/
├── 05-Documentation/
├── 06-Experiments/
└── venv/
```

---

## Step 4: Create Virtual Environment (15 minutes)

A virtual environment keeps your Python packages organized.

### 4.1 Open Terminal in VS Code

1. Press `` Ctrl+` `` (backtick, usually under Esc)
   - Or: View → Terminal
2. Terminal opens at bottom of VS Code

### 4.2 Create Virtual Environment

In the terminal, type:

```bash
python -m venv venv
```

Press Enter. This creates a `venv` folder (takes 30-60 seconds).

### 4.3 Activate Virtual Environment

**Windows PowerShell** (if you see `PS>` in terminal):
```powershell
.\venv\Scripts\Activate.ps1
```

**If you get an error about execution policy**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating again.

**Windows Command Prompt** (if you see `C:\>` in terminal):
```cmd
.\venv\Scripts\activate.bat
```

**Success looks like**:
```
(venv) PS C:\Users\Trader\AI-Agent-Learning-Hub>
```

Notice `(venv)` at the start - this means it's active!

### 4.4 Select Python Interpreter in VS Code

1. Press `Ctrl+Shift+P` (Command Palette)
2. Type: `Python: Select Interpreter`
3. Press Enter
4. Select the one that says `('venv': venv)` or has `venv` in the path

Now VS Code knows to use your virtual environment!

---

## Step 5: Install Python Packages (20 minutes)

### 5.1 Download the Files I Created

Since we're working in Windows and I created files in Linux, you need to copy them:

1. I'll provide download links for:
   - README.md
   - requirements.txt
   - .gitignore
   - And other starter files

2. Download each file
3. Place them in the `AI-Agent-Learning-Hub` folder

### 5.2 Install Packages

Make sure your venv is activated (you see `(venv)`).

In terminal:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will take 5-10 minutes. You'll see lots of text scrolling - this is normal!

**If you get errors**:
- Check internet connection
- Try: `pip install --upgrade pip`
- Install packages one at a time:
  ```bash
  pip install langchain
  pip install pandas
  pip install requests
  ```

---

## Step 6: Verify Everything Works (10 minutes)

### 6.1 Test Python

Create a test file:

1. In VS Code Explorer (left sidebar)
2. Right-click → New File
3. Name it: `test.py`
4. Type:
```python
print("Hello from Python!")
print("Setup successful! 🎉")

import pandas
import requests
print("All packages installed correctly!")
```
5. Save (Ctrl+S)
6. Right-click the file → Run Python File in Terminal

**You should see**:
```
Hello from Python!
Setup successful! 🎉
All packages installed correctly!
```

### 6.2 Test Virtual Environment

In terminal:
```bash
where python
```

**You should see**:
```
C:\Users\Trader\AI-Agent-Learning-Hub\venv\Scripts\python.exe
```

If you see `C:\Python311\python.exe` instead:
- Your venv isn't activated
- Run activation command again

---

## Step 7: Set Up Git (Optional but Recommended) (15 minutes)

### 7.1 Install Git

1. Go to https://git-scm.com/download/win
2. Download installer
3. Run installer
4. Accept all defaults
5. Finish installation

### 7.2 Configure Git

In VS Code terminal:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 7.3 Initialize Repository

In terminal (in your project folder):
```bash
git init
git add .
git commit -m "Initial setup"
```

Now your work is version controlled!

---

## Step 8: Create Your First Python Script (20 minutes)

### 8.1 Navigate to Learning Folder

1. In VS Code Explorer
2. Open: `01-Learning-Path/01-Python-Basics/`
3. Create new file: `01_hello_python.py`
4. Copy the content I created earlier (from the starter script)

### 8.2 Run Your First Script

1. Open `01_hello_python.py`
2. Press `F5` to run with debugger
   - Or right-click → Run Python File in Terminal
3. Follow along with the script!

---

## 🎯 Quick Reference Card

**Keep this handy while working:**

### Opening Project
1. Open VS Code
2. File → Open Folder
3. Select `AI-Agent-Learning-Hub`

### Activating Virtual Environment
```bash
# PowerShell
.\venv\Scripts\Activate.ps1

# Command Prompt
.\venv\Scripts\activate.bat
```

### Running Python Files
- Press `F5` (with file open)
- Or: Right-click file → Run Python File in Terminal
- Or: In terminal: `python filename.py`

### Installing Packages
```bash
# Make sure venv is active first!
pip install package-name
```

### Common VS Code Shortcuts
- `Ctrl+` ` - Open/close terminal
- `Ctrl+P` - Quick open file
- `Ctrl+Shift+P` - Command palette
- `Ctrl+S` - Save
- `Ctrl+F` - Find in file
- `Ctrl+Shift+F` - Find in all files
- `F5` - Run with debugger

---

## 🔧 Troubleshooting

### "Python not recognized"
- Reinstall Python, check "Add to PATH"
- Restart VS Code
- Restart computer

### "pip not found"
- Run: `python -m pip install --upgrade pip`

### "Cannot activate virtual environment"
- Check you're in the right folder
- Try PowerShell vs Command Prompt
- Check execution policy (see Step 4.3)

### "Import Error"
- Is venv activated? (see `(venv)` in terminal?)
- Run: `pip install -r requirements.txt` again
- Check package name spelling

### "File not found"
- Check you're in the right directory
- Use Tab key to auto-complete file names
- Check file extension (.py)

### VS Code Python not working
- Install Python extension
- Select correct interpreter (Ctrl+Shift+P → Python: Select Interpreter)
- Restart VS Code

---

## ✅ Setup Complete Checklist

Before moving on, verify:

- [ ] Python installed and in PATH
- [ ] VS Code installed with Python extension
- [ ] Project folder opened in VS Code
- [ ] Virtual environment created
- [ ] Virtual environment activated
- [ ] Packages installed from requirements.txt
- [ ] Test script runs successfully
- [ ] Git configured (optional)
- [ ] Can run Python files in VS Code

---

## 🎓 Next Steps

**You're all set up!** Now you can start learning:

1. **Read**: Main project README.md
2. **Start**: 01-Learning-Path/01-Python-Basics/README.md
3. **Practice**: Complete Module 1 exercises
4. **Build**: Work through each learning module
5. **Create**: Build your first AI agent!

---

## 📚 Additional Resources

**For complete beginners**:
- VS Code Python Tutorial: https://code.visualstudio.com/docs/python/python-tutorial
- Python Basics: https://www.w3schools.com/python/
- Virtual Environments: https://realpython.com/python-virtual-environments-a-primer/

**Video Tutorials**:
- Search YouTube: "VS Code Python setup"
- Search YouTube: "Python for beginners"

---

## 🆘 Still Having Issues?

If you're stuck:

1. **Read error messages carefully** - they usually tell you what's wrong
2. **Google the error** - Someone else has had it
3. **Check paths** - Are you in the right folder?
4. **Restart** - Close and reopen VS Code
5. **Ask for help** - Describe what you tried and what error you got

---

## 🎉 Congratulations!

You've successfully set up a professional Python development environment!

**This is a huge first step.** Many beginners struggle with setup, but you've got it done.

Now the fun part begins: **learning to code and building AI agents!**

Start with `01-Learning-Path/01-Python-Basics/` and take it one step at a time.

**Remember**: Every expert was once a beginner. You've got this! 💪
