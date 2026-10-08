"""gateway_ecosystem_report — API/AI gateway ecosystem weekly digest.

Fetches the last N days of activity from the API7 blog, the Higress site,
Higress plugin commits, and the APISIX plugin commits + CHANGELOG, then
renders a Chinese Markdown report.

Use as a CLI:

    python3 -m gateway_ecosystem_report --days 14 --out data.json
    python3 -m gateway_ecosystem_report render data.json --top 12 > report.md

Or programmatically:

    from gateway_ecosystem_report import build_report
    md = build_report(days=14, top=10)
"""
from .cli import main, build_report
from .fetchers_apiseven import fetch_apiseven_blog
from .fetchers_higress_site import fetch_higress_site_commits
from .fetchers_higress_plugins import fetch_higress_plugins
from .fetchers_apisix import fetch_apisix_plugins

__all__ = [
    "main",
    "build_report",
    "fetch_apiseven_blog",
    "fetch_higress_site_commits",
    "fetch_higress_plugins",
    "fetch_apisix_plugins",
]

__version__ = "1.0.0"
