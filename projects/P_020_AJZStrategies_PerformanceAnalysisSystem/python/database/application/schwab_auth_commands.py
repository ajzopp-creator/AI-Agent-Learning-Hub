"""schwab_auth_commands.py -- `auth` CLI command (WO-P020-E1.010).

Runs the shared OAuth login flow for a target project's own config/token
paths. Centralizes who *runs* the login -- each project still keeps its
own independently-granted token file, per shared_resources/schwab_auth.py.
"""

from __future__ import annotations

from config import AUTH_TOKEN_PATHS, SCHWAB_CONFIG_FILE


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
