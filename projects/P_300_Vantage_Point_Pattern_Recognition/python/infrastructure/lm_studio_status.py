"""
FILE: lm_studio_status.py
VERSION: 1.0
DATE: 2026-08-11
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    P_300's own thin wrapper around the Hub-level LM Studio readiness
    check (WO-P000-E5.001). application/daily_evaluate_pipeline.py calls
    this module only -- never shared_resources or integrations directly
    (Process Boundary Standard: infra change must never force an
    application change).

    Restores the P_300-owned wrapper that existed briefly at v1.11
    (2026-05-30) before v1.12 reverted the import to Hub-level directly,
    reintroducing the exact Process Boundary violation this WO closes.

CHANGELOG:
    - 2026-08-11 v1.0: Created (WO-P000-E5.001). Delegates to
      shared_resources.python_utils.lm_studio_status.check() -- no
      business logic of its own, pure passthrough.
"""
from __future__ import annotations

from shared_resources.python_utils.lm_studio_status import check as _check


def check(clean: bool = False, task_type: str | None = None) -> bool:
    """P_300 entry point for LM Studio readiness.

    See shared_resources.python_utils.lm_studio_status.check() for full
    behavior -- this wrapper exists only so application/ never imports
    outside its own project tree.
    """
    return _check(clean=clean, task_type=task_type)
