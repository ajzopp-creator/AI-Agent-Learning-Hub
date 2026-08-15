"""schwab_auth_commands.py -- `auth` CLI command (WO-P020-E1.010).

Runs the shared OAuth login flow for a target project's config/token paths.

ALL mode (added 2026-08-09): one browser login, one grant, propagated to
every registered project's token file. This supersedes the original
per-project-separate-grant design -- see the Scope amendment in
WO-P020-E1.010. Reason: Schwab revokes at the APP REGISTRATION level, not
the token-file level, so N separate logins against one registration leave
only the most recent one working (confirmed by controlled test 2026-08-09).
Separate token FILES were never the problem; separate GRANTS were.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from config import AUTH_TOKEN_PATHS, SCHWAB_CONFIG_FILE

# Which project's path receives the live login. Every other registered
# project gets a byte copy of the resulting file.
PRIMARY_PROJECT = "P_020"


def cmd_auth(project: str) -> int:
    """Run Schwab OAuth for the given project, writing its own token file.

    Args:
        project: Project key -- "P_020" or "P_400".

    Returns:
        0 on success.

    Raises:
        ValueError: If project is not a recognized key.
    """
    from shared_resources.python_utils.schwab_auth import run_auth

    if project not in AUTH_TOKEN_PATHS:
        raise ValueError(
            f"Unknown project '{project}'. Valid: {list(AUTH_TOKEN_PATHS)}"
        )

    token_path = AUTH_TOKEN_PATHS[project]
    run_auth(SCHWAB_CONFIG_FILE, token_path)
    return 0


def _verify_token_file(path: Path, expected_bytes: bytes) -> None:
    """Confirm a propagated copy landed intact.

    Durable-signal rule (peh-handoff): a write returning cleanly is not
    proof. Checks existence, byte-identity against the source, and that
    the result still parses as JSON.

    Args:
        path: Destination token file.
        expected_bytes: Source file's exact bytes.

    Raises:
        RuntimeError: On any mismatch -- caller must not report success.
    """
    if not path.exists():
        raise RuntimeError(f"Token copy missing: {path}")

    actual = path.read_bytes()
    if actual != expected_bytes:
        raise RuntimeError(
            f"Token copy differs from source: {path} "
            f"({len(actual)} bytes vs {len(expected_bytes)})"
        )

    try:
        json.loads(actual.decode("utf-8"))
    except Exception as e:
        raise RuntimeError(f"Token copy is not valid JSON: {path} -- {e}") from e


def cmd_auth_all() -> int:
    """One login, one grant, propagated to every registered project.

    Runs the browser flow once against PRIMARY_PROJECT's token path, then
    byte-copies that file to every other path in AUTH_TOKEN_PATHS and
    verifies each copy. Adding a project later is one AUTH_TOKEN_PATHS
    entry -- no change here.

    Returns:
        0 on success.

    Raises:
        RuntimeError: If the primary login produced no file, or any copy
            failed verification. Partial propagation is a failure, not a
            warning -- a silently-missed project is exactly the failure
            mode this command exists to eliminate.
    """
    from shared_resources.python_utils.schwab_auth import run_auth

    primary_path = AUTH_TOKEN_PATHS[PRIMARY_PROJECT]
    targets = [k for k in AUTH_TOKEN_PATHS if k != PRIMARY_PROJECT]

    print(f"One login for {len(AUTH_TOKEN_PATHS)} project(s): "
          f"{', '.join(AUTH_TOKEN_PATHS)}")
    print(f"Browser login writes: {PRIMARY_PROJECT}")

    run_auth(SCHWAB_CONFIG_FILE, primary_path)

    if not primary_path.exists():
        raise RuntimeError(
            f"Login reported success but no token file at {primary_path}"
        )

    source_bytes = primary_path.read_bytes()
    print(f"[OK] {PRIMARY_PROJECT}: {primary_path.name} "
          f"({len(source_bytes)} bytes)")

    for key in targets:
        dest = AUTH_TOKEN_PATHS[key]
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(primary_path, dest)
        _verify_token_file(dest, source_bytes)
        print(f"[OK] {key}: {dest.name} -- verified byte-identical")

    print(f"Done. {len(AUTH_TOKEN_PATHS)} project(s) share one grant.")
    return 0
