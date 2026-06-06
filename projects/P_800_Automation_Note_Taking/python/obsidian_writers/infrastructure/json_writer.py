"""infrastructure/json_writer.py — Write raw signal packets as JSON files.

Used by P400SIG (Enhancement 1): validate → build → json_writer path.
No verdict normalization, no provenance, no frontmatter — raw signal output.
"""

import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


def write_signal(schema_name: str, data: dict[str, Any], output_path: str | Path) -> bool:
    """Write signal packet as raw JSON file.
    
    Args:
        schema_name: Schema identifier (e.g., "P400SIG")
        data: Signal data dict
        output_path: File path for JSON output
        
    Returns:
        bool: True if write succeeded, False otherwise
    """
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        log.info(f"✓ Signal written: {output_path}")
        return True
        
    except Exception as e:
        log.error(f"✗ Signal write failed: {e}")
        return False