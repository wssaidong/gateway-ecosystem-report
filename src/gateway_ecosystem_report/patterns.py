"""Shared regex patterns used by the fetchers and the tests.

Centralising the patterns here means the tests can assert the patterns
without having to import the fetcher functions and trigger a network
call.
"""
from __future__ import annotations
import re

# Conventional commit scope:  feat(<plugin>): subject
PLUGIN_RE = re.compile(
    r"^(?:feat|fix|refactor|chore|docs|perf)\(([a-z][a-z0-9-]*)\):"
)

# CHANGELOG / release-body line announcing a new plugin.
# Matches `feat: add the <name> plugin` and `feat(<scope>): add the <name> plugin`.
NEW_PLUGIN_RE = re.compile(
    r"^feat(?:\(([a-z][a-z0-9-]*)\))?:\s*add the [`'\"]([a-z][a-z0-9-]*)[`'\"][^.]*plugin"
)

# apiseven blog HTML — current next.js export schema
LIST_RE = re.compile(r'"list":\[(.*?)\]\},"__N_SSG":', re.DOTALL)
# apiseven blog HTML — legacy schema (older snapshots)
ARTICLES_RE = re.compile(r'"articles":\[(.*?)\],"page":', re.DOTALL)
