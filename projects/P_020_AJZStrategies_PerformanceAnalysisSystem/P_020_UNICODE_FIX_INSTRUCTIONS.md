# P_020 - UNICODE CHARACTER FIX

## 🎯 **The Problem:**

The parser uses fancy checkmarks (✓) that Windows Command Prompt can't display!

```
Error: UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'
```

---

## ✅ **TWO SOLUTIONS:**

### **Solution 1: Use UTF-8 Batch File** ⭐ EASIEST

**File:** `P_020_Test_Full_Workflow_UTF8.bat`

This version sets UTF-8 encoding automatically!

**Run this instead:**
```batch
P_020_Test_Full_Workflow_UTF8.bat Paper
```

**What it does:**
- Sets UTF-8 encoding: `chcp 65001`
- Sets Python UTF-8: `PYTHONIOENCODING=utf-8`
- Should handle the checkmarks now!

---

### **Solution 2: Fix the Parser Script** (if UTF-8 doesn't work)

**Edit:** `python\parsers\P_020_TOS_Parser_v2.py`

**Find lines with checkmarks (✓) and replace with [OK]:**

```python
# OLD (line 403):
print(f"  ✓ Loaded {len(df)} transactions")

# NEW:
print(f"  [OK] Loaded {len(df)} transactions")
```

**Replace all instances:**
- `✓` → `[OK]`
- `✅` → `[OK]`
- `❌` → `[ERROR]`
- Any other fancy Unicode characters

---

## 🚀 **Try This Now:**

```batch
P_020_Test_Full_Workflow_UTF8.bat Paper
```

**This should work!** The UTF-8 encoding will let Windows display the checkmarks! ✓

---

## 💡 **Why This Happened:**

Windows Command Prompt uses CP1252 encoding (old Windows encoding) by default.

Unicode characters like ✓ ✅ ❌ don't exist in CP1252.

Setting UTF-8 (chcp 65001) fixes it!

---

## 📥 **Download:**

✅ **P_020_Test_Full_Workflow_UTF8.bat** - Has UTF-8 encoding fix built-in!

---

**Try it and let me know!** 🚀
