# Troubleshooting: PowerShell vs CMD Issues

## The SETUP.bat Problem - SOLVED ✓

### What Happened?

When you tried to run `SETUP.bat` in PowerShell, you got this error:
```
The Setup command may only be used inside a Describe block.
```

### Why?

PowerShell has a built-in testing framework called **Pester** that reserves "Setup" as a special command. When you type `SETUP.bat`, PowerShell tried to run the Pester Setup command instead of your batch file.

### Solution: Renamed to INSTALL.bat

We renamed the file from `SETUP.bat` to `INSTALL.bat` to avoid this conflict.

---

## How to Run .bat Files in PowerShell

### Option 1: Use .\ prefix (RECOMMENDED)
```powershell
.\INSTALL.bat
.\TEST_LMSTUDIO.bat
.\transcribe.bat "audio.mp3"
```

### Option 2: Use cmd /c
```powershell
cmd /c INSTALL.bat
cmd /c TEST_LMSTUDIO.bat
```

### Option 3: Just double-click the .bat file in File Explorer
This always works and runs in CMD automatically.

---

## Better: Use PowerShell Scripts

We also created PowerShell-native versions:

### Installation
```powershell
# Instead of INSTALL.bat, use:
.\Install-Packages.ps1
```

### Testing
```powershell
# Instead of TEST_LMSTUDIO.bat, use:
.\Test-LMStudio.ps1  # (if we create this)
```

---

## Quick Reference: Which to Use?

| Task | In CMD | In PowerShell |
|------|--------|---------------|
| Install | `INSTALL.bat` | `.\INSTALL.bat` or `.\Install-Packages.ps1` |
| Test | `TEST_LMSTUDIO.bat` | `.\TEST_LMSTUDIO.bat` |
| Transcribe | `transcribe.bat "file.mp3"` | `.\transcribe.bat "file.mp3"` |
| Examples | `EXAMPLES.bat` | `.\EXAMPLES.bat` |

---

## Pro Tip: Make PowerShell Run .bat Files Like CMD

Add this to your PowerShell profile to automatically run .bat files:

```powershell
# Edit your profile
notepad $PROFILE

# Add this function:
function Run-BatFile {
    param([string]$file)
    if (Test-Path $file) {
        cmd /c $file
    }
}

# Then you can use:
Run-BatFile INSTALL.bat
```

But honestly, just using `.\filename.bat` is simpler!

---

## Current Installation Instructions

### PowerShell Users (RECOMMENDED):
```powershell
cd C:\Users\Trader\AI-Agent-Learning-Hub\03-Local-LLM\Audio-Transcription
.\Install-Packages.ps1
```

### CMD Users:
```cmd
cd C:\Users\Trader\AI-Agent-Learning-Hub\03-Local-LLM\Audio-Transcription
INSTALL.bat
```

### Anyone (No Terminal):
Just double-click `INSTALL.bat` in File Explorer!

---

## Summary

✓ **Problem:** PowerShell reserved word conflict with "SETUP"
✓ **Solution:** Renamed to INSTALL.bat  
✓ **Bonus:** Created PowerShell-native Install-Packages.ps1
✓ **Going forward:** Always use `.\filename.bat` in PowerShell

---

**You're all set!** Run `.\INSTALL.bat` or `.\Install-Packages.ps1` to continue.
