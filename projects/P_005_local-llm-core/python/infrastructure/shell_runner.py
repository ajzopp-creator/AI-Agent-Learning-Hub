"""Infrastructure execution runners for local file I/O and PowerShell commands."""

import math
import subprocess
from pathlib import Path
from typing import List

from domain.tool_registry import register_tool


@register_tool
def calculate_compound_interest(principal: float, rate: float, time_years: int) -> float:
    """Calculate compound interest given principal, annual rate (decimal), and years."""
    return round(principal * math.pow((1 + rate), time_years), 2)


@register_tool
def list_directory_contents(dir_path: str = ".") -> List[str]:
    """List all files and subfolders in a target directory."""
    target = Path(dir_path).resolve()
    if not target.exists():
        return [f"ERROR: Directory '{dir_path}' does not exist."]
    return [item.name for item in target.iterdir()]


@register_tool
def read_text_file(file_path: str, max_lines: int = 150) -> str:
    """Read contents of a text file up to a specified line limit."""
    target = Path(file_path).resolve()
    if not target.exists() or not target.is_file():
        return f"ERROR: File '{file_path}' does not exist."
    try:
        with open(target, "r", encoding="utf-8-sig", errors="replace") as f:
            lines = [f.readline() for _ in range(max_lines)]
            return "".join([line for line in lines if line])
    except Exception as e:
        return f"ERROR reading file: {str(e)}"


@register_tool
def write_text_file(file_path: str, content: str) -> str:
    """Write text content to a local file with UTF-8 encoding."""
    try:
        target = Path(file_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        return f"SUCCESS: File written to '{target}'"
    except Exception as e:
        return f"ERROR writing file: {str(e)}"


@register_tool
def execute_powershell_command(command: str, timeout_seconds: int = 30) -> str:
    """Execute a local PowerShell command and return stdout/stderr."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        output = result.stdout.strip()
        error = result.stderr.strip()
        if result.returncode != 0:
            return f"EXIT CODE {result.returncode}\nSTDERR:\n{error}\nSTDOUT:\n{output}"
        return output if output else "SUCCESS (No Output)"
    except subprocess.TimeoutExpired:
        return f"ERROR: Command timed out after {timeout_seconds} seconds."
    except Exception as e:
        return f"ERROR executing command: {str(e)}"