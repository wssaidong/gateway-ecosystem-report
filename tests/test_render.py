"""End-to-end tests for the renderer using fixture data (stdlib only)."""
import json
import tempfile
import unittest
from pathlib import Path

from gateway_ecosystem_report.render_part1 import (
    section_apiseven, section_higress_site,
)
from gateway_ecosystem_report.render_part2 import (
    section_higress_plugins, section_apisix_plugins, section_kong, footer,
)
from gateway_ecosystem_report.cli import build_report, _fetch, _render


FIXTURE = {
    "meta": {"date": "2026-10-08", "window_days": 14},
    "apiseven_articles": [
        {
            "title": "API7 网关 3.10.7: example",
            "slug": "/blog/example",
            "published_at": "2026-10-01",
            "tags": ["API7 网关", "API 安全"],
            "url": "https://www.apiseven.com/blog/example",
        }
    ],
    "apiseven_recent": [
        {
            "title": "Older", "slug": "/blog/older",
            "published_at": "2026-09-22",
            "tags": ["older"],
            "url": "https://www.apiseven.com/blog/older",
        }
    ],
    "higress_site_commits": [
        {
            "sha": "abc1234", "date": "2026-10-04T10:43:49Z",
            "author": "澄潭", "message": "chore(release): bump",
            "url": "https://github.com/.../commit/abc1234",
        }
    ],
    "higress_plugins": [
        {
            "sha": "deadbee", "date": "2026-09-29T08:46:58Z",
            "author": "澄潭",
            "message": "fix(mcp-session): write back assembled SSE",
            "plugin": "mcp-session",
            "url": "https://github.com/.../commit/deadbee",
        }
    ],
    "apisix_plugins": {
        "commits": [
            {
                "sha": "cafef00", "date": "2026-10-08T05:58:11Z",
                "author": "AlinsRan",
                "message": "feat(prometheus): add service and service_id",
                "plugin": "prometheus",
                "url": "https://github.com/apache/apisix/commit/cafef00",
            }
        ],
        "new_plugins": [
            {
                "name": "openapi-to-mcp", "tag": "3.19.0",
                "source": "changelog:3.19.0",
                "detail": "feat: add the `openapi-to-mcp` plugin",
            }
        ],
    },
    "kong": {
        "repo": {
            "stars": 44340, "open_issues": 225,
            "default_branch": "master", "pushed_at": "2026-10-19T02:45:09Z",
        },
        "commits": [
            {
                "sha": "abc0123", "date": "2026-10-19T02:44:32Z",
                "author": "Kong CI",
                "message": "chore(ci): migrate Docker Hub login to OIDC (#15044)",
                "scope": "ci",
                "url": "https://github.com/Kong/kong/commit/abc0123",
            }
        ],
        "releases": [
            {
                "tag": "3.9.4", "published_at": "2026-10-12T07:27:48Z",
                "url": "https://github.com/Kong/kong/releases/tag/3.9.4",
            }
        ],
        "changelog": [
            {
                "version": "3.9.4", "date": "2026-10-12T07:27:48Z",
                "counts": {"Fixes": 1},
                "entries": [
                    {
                        "component": "Kong", "category": "Fixes",
                        "area": "Clustering",
                        "text": "Fixed a SQL injection in the clustering RPC "
                                "procedure",
                        "ref": "#15024",
                        "ref_url": "https://github.com/Kong/kong/pull/15024",
                    }
                ],
            }
        ],
        "unreleased_count": 2,
        "since": "2026-10-04T00:00:00Z",
    },
}


class TestApisevenSection(unittest.TestCase):
    def test_in_window_renders_article(self):
        md = section_apiseven(
            FIXTURE["apiseven_articles"], FIXTURE["apiseven_recent"], 10
        )
        self.assertIn("API7 网关 3.10.7: example", md)
        self.assertIn("窗口内共", md)

    def test_empty_in_window_shows_recent(self):
        md = section_apiseven([], FIXTURE["apiseven_recent"], 10)
        self.assertIn("窗口内没有新文章", md)
        self.assertIn("Older", md)


class TestHigressSiteSection(unittest.TestCase):
    def test_renders_commits(self):
        md = section_higress_site(FIXTURE["higress_site_commits"], 10)
        self.assertIn("abc1234", md)
        self.assertIn("chore(release): bump", md)

    def test_empty(self):
        md = section_higress_site([], 10)
        self.assertIn("没有任何提交", md)


class TestHigressPluginsSection(unittest.TestCase):
    def test_renders_commits(self):
        md = section_higress_plugins(FIXTURE["higress_plugins"], 10)
        self.assertIn("mcp-session", md)
        self.assertIn("Top commits", md)

    def test_empty(self):
        md = section_higress_plugins([], 10)
        self.assertIn("没有针对", md)


class TestApisixPluginsSection(unittest.TestCase):
    def test_renders_new_plugin(self):
        md = section_apisix_plugins(FIXTURE["apisix_plugins"], 10)
        self.assertIn("openapi-to-mcp", md)
        self.assertIn("新增插件", md)
        self.assertIn("prometheus", md)

    def test_empty(self):
        md = section_apisix_plugins({"commits": [], "new_plugins": []}, 10)
        self.assertIn("没有新插件", md)


class TestKongSection(unittest.TestCase):
    def test_renders_three_dimensions(self):
        md = section_kong(FIXTURE["kong"], 10)
        # 项目动向
        self.assertIn("44,340", md)
        self.assertIn("changelog/unreleased", md)
        # 提交内容
        self.assertIn("chore(ci): migrate Docker Hub login to OIDC", md)
        self.assertIn("`ci`", md)
        # 版本更新
        self.assertIn("3.9.4", md)
        self.assertIn("窗口内 ✅", md)
        self.assertIn("[Fixes/Clustering]", md)
        self.assertIn("#15024", md)

    def test_empty_data_notes_missing_key(self):
        md = section_kong({}, 10)
        self.assertIn("早于 Kong 追踪", md)

    def test_no_commits_still_renders_versions(self):
        data = dict(FIXTURE["kong"], commits=[])
        md = section_kong(data, 10)
        self.assertIn("没有提交", md)
        self.assertIn("3.9.4", md)

    def test_no_window_release_expands_newest_as_context(self):
        data = dict(FIXTURE["kong"], since="2026-12-01T00:00:00Z")
        md = section_kong(data, 10)
        self.assertIn("窗口外参考", md)
        self.assertIn("[Fixes/Clustering]", md)


class TestRenderEndToEnd(unittest.TestCase):
    def test_render_from_file(self):
        with tempfile.TemporaryDirectory() as td:
            data_file = Path(td) / "data.json"
            data_file.write_text(json.dumps(FIXTURE, ensure_ascii=False))
            # Simulate the CLI
            import argparse
            args = argparse.Namespace(input=str(data_file), top=10)
            import sys
            from io import StringIO
            buf = StringIO()
            saved = sys.stdout
            sys.stdout = buf
            try:
                rc = _render(args)
            finally:
                sys.stdout = saved
            self.assertEqual(rc, 0)
            out = buf.getvalue()
            self.assertIn("# 🌐 API/AI 网关生态周报", out)
            self.assertIn("openapi-to-mcp", out)
            self.assertIn("mcp-session", out)
            self.assertIn("API7 网关 3.10.7: example", out)
            self.assertIn("Kong Gateway", out)
            self.assertIn("3.9.4", out)


if __name__ == "__main__":
    unittest.main()
