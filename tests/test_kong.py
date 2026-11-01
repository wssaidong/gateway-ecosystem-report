"""Tests for the Kong fetcher's pure parsing logic (stdlib only)."""
import unittest

from gateway_ecosystem_report.fetchers_kong import parse_changelog, _scope


CHANGELOG_FIXTURE = """# Table of Contents

- [3.9.4](#394)
- [3.9.3](#393)

## Unreleased

Individual unreleased changelog entries can be located at
[changelog/unreleased](changelog/unreleased).

## 3.9.4

### Kong

#### Fixes

##### Clustering

- Fixed an issue where a SQL injection vulnerability existed in the
 clustering RPC procedure ([CVE-2026-1907](https://nvd.nist.gov/vuln/detail/cve-2026-1907)).
 [#15024](https://github.com/Kong/kong/pull/15024)

## 3.9.3

### Kong

#### Fixes
##### Core

- Applied upstream nginx security patches (CVE-2026-49975).
 [#14895](https://github.com/Kong/kong/issues/14895)

#### Dependencies
##### Core

- Bumped luarocks from 3.11.1 to 3.12.2.
 [#14672](https://github.com/Kong/kong/issues/14672)

## Previous releases

See the [old changelog](https://github.com/Kong/kong/blob/master/CHANGELOG.old.md).
"""


class TestParseChangelog(unittest.TestCase):
    def setUp(self):
        self.versions = parse_changelog(CHANGELOG_FIXTURE)

    def test_versions_in_order(self):
        self.assertEqual(
            [v["version"] for v in self.versions], ["3.9.4", "3.9.3"]
        )

    def test_entry_path_component_category_area(self):
        entry = self.versions[0]["entries"][0]
        self.assertEqual(entry["component"], "Kong")
        self.assertEqual(entry["category"], "Fixes")
        self.assertEqual(entry["area"], "Clustering")
        self.assertIn("SQL injection", entry["text"])

    def test_ref_stripped_from_text_but_kept_as_ref(self):
        entry = self.versions[0]["entries"][0]
        self.assertEqual(entry["ref"], "#15024")
        self.assertIn("pull/15024", entry["ref_url"])
        self.assertNotIn("[#15024]", entry["text"])
        # inline CVE link must survive the strip
        self.assertIn("CVE-2026-1907", entry["text"])

    def test_multiple_categories_counted_by_caller_shape(self):
        v = self.versions[1]
        self.assertEqual(len(v["entries"]), 2)
        cats = [e["category"] for e in v["entries"]]
        self.assertEqual(cats, ["Fixes", "Dependencies"])

    def test_previous_releases_tail_not_swallowed(self):
        for v in self.versions:
            for e in v["entries"]:
                self.assertNotIn("old changelog", e["text"])

    def test_unreleased_and_toc_skipped(self):
        texts = " ".join(e["text"] for v in self.versions for e in v["entries"])
        self.assertNotIn("unreleased", texts)


class TestScope(unittest.TestCase):
    def test_scope(self):
        self.assertEqual(_scope("chore(ci/cd): x (#1)"), "ci/cd")
        self.assertEqual(_scope("docs(COPYRIGHT): y"), "COPYRIGHT")
        self.assertEqual(_scope("fix: no scope"), "fix")
        self.assertEqual(_scope("Merge commit from fork"), "misc")


if __name__ == "__main__":
    unittest.main()
