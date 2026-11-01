"""Tests for the regex patterns in `patterns.py` (stdlib only)."""
import unittest

from gateway_ecosystem_report.patterns import (
    PLUGIN_RE, NEW_PLUGIN_RE, LIST_RE, ARTICLES_RE, KONG_COMMIT_RE,
    KONG_REF_RE,
)


class TestPluginRe(unittest.TestCase):
    def test_matches_feat(self):
        m = PLUGIN_RE.match("feat(mcp-server): add foo")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "mcp-server")

    def test_matches_fix(self):
        m = PLUGIN_RE.match("fix(ai-proxy): bar")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "ai-proxy")

    def test_matches_chore_refactor_docs_perf(self):
        for prefix in ("chore", "refactor", "docs", "perf"):
            with self.subTest(prefix=prefix):
                m = PLUGIN_RE.match(f"{prefix}(release): bump")
                self.assertIsNotNone(m, prefix)
                self.assertEqual(m.group(1), "release")

    def test_no_match_standalone(self):
        self.assertIsNone(PLUGIN_RE.match("update by robot"))

    def test_no_match_capitalized_scope(self):
        self.assertIsNone(PLUGIN_RE.match("feat(AI-Proxy): bar"))


class TestNewPluginRe(unittest.TestCase):
    def test_backtick_quoted(self):
        m = NEW_PLUGIN_RE.match("feat: add the `openapi-to-mcp` plugin,")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(2), "openapi-to-mcp")

    def test_with_scope(self):
        m = NEW_PLUGIN_RE.match(
            "feat(websocket): add the `websocket-proxy` plugin to"
        )
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "websocket")
        self.assertEqual(m.group(2), "websocket-proxy")

    def test_no_match_when_no_plugin_keyword(self):
        self.assertIsNone(
            NEW_PLUGIN_RE.match("feat: add the `openapi-to-mcp` bridge")
        )


class TestBlogHtmlRegexes(unittest.TestCase):
    def test_list_block_extracted(self):
        # Real HTML has the structure  ...]}],\"__N_SSG\":true},... —
        # the inner } closes the last article object, the next ] closes the
        # list array, the final } closes the pageProps object, then __N_SSG.
        html = '"list":[{"title":"A"}]},"__N_SSG":true'
        m = LIST_RE.search(html)
        self.assertIsNotNone(m)
        self.assertIn('"title":"A"', m.group(1))

    def test_articles_block_legacy(self):
        html = '"articles":[{"title":"A"}],"page":"/blog"'
        m = ARTICLES_RE.search(html)
        self.assertIsNotNone(m)
        self.assertIn('"title":"A"', m.group(1))


class TestKongCommitRe(unittest.TestCase):
    def test_scope_with_slash(self):
        m = KONG_COMMIT_RE.match("chore(ci/cd): pass correct tag (#15034)")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(2), "ci/cd")

    def test_uppercase_scope(self):
        m = KONG_COMMIT_RE.match("docs(COPYRIGHT): update copyright (#15017)")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(2), "COPYRIGHT")

    def test_types_beyond_the_plugin_grammar(self):
        for msg, scope in [
            ("tests(ldap): use local AD fixtures (#15046)", "ldap"),
            ("fix(ci): preserve runtimes (#15043)", "ci"),
            ("chore(deps): bump openssl (#15004)", "deps"),
        ]:
            with self.subTest(msg=msg):
                m = KONG_COMMIT_RE.match(msg)
                self.assertIsNotNone(m)
                self.assertEqual(m.group(2), scope)

    def test_scope_optional(self):
        m = KONG_COMMIT_RE.match("fix: something without a scope")
        self.assertIsNotNone(m)
        self.assertIsNone(m.group(2))

    def test_no_match_without_colon(self):
        self.assertIsNone(KONG_COMMIT_RE.match("Merge commit from fork"))
        self.assertIsNone(KONG_COMMIT_RE.match("fixing stuff asap"))


class TestKongRefRe(unittest.TestCase):
    def test_extracts_pr_number_and_url(self):
        m = KONG_REF_RE.search("Fixed X. [#15024](https://github.com/Kong/kong/pull/15024)")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "15024")
        self.assertIn("pull/15024", m.group(2))


if __name__ == "__main__":
    unittest.main()
