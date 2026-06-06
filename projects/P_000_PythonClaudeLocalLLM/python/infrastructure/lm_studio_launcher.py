"""
LM Studio Launcher
Finds and starts LM Studio if it's not already running.
Handles the full startup workflow: launch → wait for health → proceed.
"""

import subprocess
import asyncio
import logging
from pathlib import Path
from typing import Optional
from infrastructure.lm_studio_api import check_lm_studio_health
from config import LOG_FILE

# ── LOGGING SETUP ─────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
handler = logging.FileHandler(LOG_FILE)
handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ── COMMON LM STUDIO INSTALLATION PATHS ───────────────────────────────────────
POSSIBLE_LM_STUDIO_PATHS = [
    Path(r"C:\Program Files\LM Studio\LM Studio.exe"),
    Path(r"C:\Program Files (x86)\LM Studio\LM Studio.exe"),
    Path(r"C:\Program Files\LM Studio\lm-studio.exe"),
    Path(r"C:\Program Files (x86)\LM Studio\lm-studio.exe"),
    Path.home() / "AppData" / "Local" / "LM Studio" / "LM Studio.exe",
    Path.home() / "AppData" / "Local" / "Programs" / "LM Studio" / "LM Studio.exe",
]


def find_lm_studio_executable() -> Optional[Path]:
    """
    Search common installation paths for LM Studio executable.
    
    Returns:
        Path to LM Studio.exe if found, None otherwise.
    """
    for path in POSSIBLE_LM_STUDIO_PATHS:
        if path.exists():
            logger.info(f"Found LM Studio at: {path}")
            return path
    
    logger.warning("LM Studio executable not found in common paths")
    return None


async def start_lm_studio() -> bool:
    """
    Start LM Studio if it's not already running.
    Waits up to 30 seconds for it to become responsive.
    
    Returns:
        True if LM Studio is now running and healthy, False otherwise.
    """
    # Check if already running
    if await check_lm_studio_health():
        logger.info("LM Studio is already running")
        return True
    
    # Find executable
    exe_path = find_lm_studio_executable()
    if not exe_path:
        logger.error(
            "LM Studio executable not found. "
            "Install LM Studio or add its path to POSSIBLE_LM_STUDIO_PATHS"
        )
        return False
    
    # Launch it
    try:
        logger.info(f"Starting LM Studio from: {exe_path}")
        subprocess.Popen(
            str(exe_path),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        logger.error(f"Failed to start LM Studio: {e}")
        return False
    
    # Wait for it to become responsive (up to 30 seconds)
    max_attempts = 30
    for attempt in range(max_attempts):
        await asyncio.sleep(1)
        
        if await check_lm_studio_health():
            logger.info(f"LM Studio is now healthy (took {attempt + 1}s)")
            return True
        
        if (attempt + 1) % 5 == 0:
            logger.info(f"Waiting for LM Studio... ({attempt + 1}s)")
    
    logger.error(f"LM Studio did not start within {max_attempts} seconds")
    return False


async def ensure_lm_studio_running() -> bool:
    """
    Guarantee LM Studio is running — starts it if necessary.
    
    Returns:
        True if LM Studio is running, False if startup failed.
    """
    return await start_lm_studio()
