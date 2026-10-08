"""GitHub API helper.

All API calls go through `gh api` so that the `gh` CLI handles authentication
and respects the local user's token without exposing it to this process.

The fetcher is intentionally simple: it shells out once per endpoint and
returns parsed JSON. A future async refactor can swap the implementation
without changing the call sites.
"""
from __future__ import annotations
import json
import subprocess
from typing import Any

GH_CMD = ["gh", "api", "-H", "Accept: application/vnd.github+json"]


def gh(path: str) -> Any:
    """Run `gh api <path>` and return parsed JSON, or None on failure."""
    out = subprocess.run(GH_CMD + [path], capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return None
