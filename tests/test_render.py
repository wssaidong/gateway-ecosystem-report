"""End-to-end tests for the renderer using fixture data (stdlib only)."""
import json
import tempfile
import unittest
from pathlib import Path

from gateway_ecosystem_report.render_part1 import (
    section_apiseven, section_higress_site,
)
from gateway_ecosystem_report.render_part2 import (
    section_higress_plugins, section_apisix_plugins, footer,
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


if __name__ == "__main__":
    unittest.main()
