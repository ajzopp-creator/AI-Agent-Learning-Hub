# Phase 1: Python Basics 🐍

**Goal**: Get comfortable with Python fundamentals needed for building AI agents

**Estimated Time**: 1-2 weeks  
**Prerequisites**: None - complete beginner friendly!

## 📋 What You'll Learn

1. Variables, data types, and basic operations
2. Lists, dictionaries, and data structures
3. Functions and how to organize code
4. Working with files
5. Error handling (try/except)
6. Basic API calls with requests library

## 🎯 Learning Modules

### Module 1: Hello Python (Day 1-2)
**File**: `01_hello_python.py`

Topics:
- Running Python in VS Code
- Variables and print statements
- Basic math operations
- String manipulation

**Exercise**: Create a simple calculator script

---

### Module 2: Data Structures (Day 3-4)
**File**: `02_data_structures.py`

Topics:
- Lists and list operations
- Dictionaries (key-value pairs)
- For loops and while loops
- List comprehensions (Python magic!)

**Exercise**: Build a stock portfolio tracker (using fake data)

---

### Module 3: Functions (Day 5-6)
**File**: `03_functions.py`

Topics:
- Writing your own functions
- Parameters and return values
- Organizing code into modules
- Importing functions

**Exercise**: Create reusable functions for risk calculations

---

### Module 4: Working with Files (Day 7-8)
**File**: `04_files.py`

Topics:
- Reading and writing text files
- Working with CSV files
- JSON data (used everywhere in APIs!)
- Path handling

**Exercise**: Read a CSV of trades and calculate total P&L

---

### Module 5: Error Handling (Day 9-10)
**File**: `05_error_handling.py`

Topics:
- Try/except blocks
- Different types of errors
- Logging errors
- Graceful failure

**Exercise**: Make your scripts handle bad data without crashing

---

### Module 6: Your First API Call (Day 11-14)
**File**: `06_first_api.py`

Topics:
- What is an API?
- Using the `requests` library
- Reading API responses (JSON)
- Environment variables for API keys

**Exercise**: Connect to a free finance API (Alpha Vantage or similar)

---

## 🚀 Getting Started

### Step 1: Open VS Code
1. Open VS Code
2. File → Open Folder → Select `AI-Agent-Learning-Hub`
3. Open Terminal in VS Code: View → Terminal (or Ctrl+`)

### Step 2: Activate Your Virtual Environment
```bash
# In VS Code terminal:
.\venv\Scripts\activate

# You should see (venv) appear in your prompt
```

### Step 3: Start with Module 1
```bash
# Navigate to this folder
cd 01-Learning-Path\01-Python-Basics

# Run your first script
python 01_hello_python.py
```

### Step 4: Follow Along
- Open each .py file in VS Code
- Read the comments (lines starting with #)
- Run the code
- Complete the exercises
- Check your answers in the solutions folder

---

## 📚 Recommended Resources

**For Complete Beginners**:
- [Python Official Tutorial](https://docs.python.org/3/tutorial/)
- [W3Schools Python](https://www.w3schools.com/python/)
- [Real Python Tutorials](https://realpython.com/)

**Interactive Learning**:
- [Codecademy Python Course](https://www.codecademy.com/learn/learn-python-3) (first part is free)
- [Python Tutor](https://pythontutor.com/) - Visualize code execution

**Quick Reference**:
- [Python Cheat Sheet](https://www.pythoncheatsheet.org/)

---

## ✅ Completion Checklist

Before moving to Phase 2, make sure you can:

- [ ] Write and run a Python script in VS Code
- [ ] Create and use variables
- [ ] Work with lists and dictionaries
- [ ] Write your own functions
- [ ] Read and write files
- [ ] Handle errors with try/except
- [ ] Make a simple API call
- [ ] Understand what JSON is

**Self-Test**: Can you write a script that:
1. Reads a CSV file of stock symbols
2. Makes an API call for each stock
3. Prints the current price
4. Handles errors if the API fails

If yes → You're ready for Phase 2! 🎉

---

## 🆘 Stuck? Common Issues

**Error: "python is not recognized"**
- Install Python from python.org
- Make sure to check "Add Python to PATH" during installation

**Error: "No module named X"**
- Make sure your virtual environment is activated
- Run: `pip install -r requirements.txt`

**Code not running**:
- Check for indentation errors (Python is picky about spaces!)
- Look at the error message - it tells you the line number
- Use print() statements to debug

**VS Code issues**:
- Make sure you've selected the correct Python interpreter (bottom right corner)
- It should show "3.x.x ('venv')"

---

## 📝 Notes Space

Use this section for your own notes as you learn:

```
My Learning Notes:
- Date started: ___________
- Things I found easy: 
- Things I need to review:
- Questions:




```

---

**Next**: Once comfortable, move to `02-API-Integration/`  
**Estimated completion**: 2 weeks at 1-2 hours/day
