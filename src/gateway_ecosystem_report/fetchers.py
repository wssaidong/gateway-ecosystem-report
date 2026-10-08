"""Regex constants re-exported for backwards compatibility.

New code should import directly from `gateway_ecosystem_report.patterns`.
"""
from .patterns import (
    PLUGIN_RE,
    NEW_PLUGIN_RE,
    LIST_RE,
    ARTICLES_RE,
)

# Compat aliases for code that used the old underscore-prefixed names.
_LIST_RE = LIST_RE
_ARTICLES_RE = ARTICLES_RE

__all__ = [
    "PLUGIN_RE",
    "NEW_PLUGIN_RE",
    "LIST_RE",
    "ARTICLES_RE",
]
