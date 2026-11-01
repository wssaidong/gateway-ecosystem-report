# Changelog

All notable changes to this skill are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/), and this project
adheres to [Semantic Versioning](https://semver.org/).

## [1.1.0] - 2026-11-02

### Added

- Kong Gateway (`Kong/kong`) as source #5, tracked at the same granularity
  as the existing gateways across three dimensions:
  - 项目动向 — repo metadata (stars / open issues / default branch /
    pushed_at), whole-window commits grouped by conventional-commit scope,
    and the `changelog/unreleased/` queue size as the next-release hint.
  - 提交内容 — commit rows in the same shape as the other sources, with
    `scope` instead of `plugin`.
  - 版本更新 — latest releases plus per-version entries parsed from the
    repo-root `CHANGELOG.md` (component / category / area / text / PR ref),
    with in-window versions expanded and out-of-window ones summarised.
- `fetchers_kong.py`, `section_kong` in the renderer, `KONG_COMMIT_RE` /
  `KONG_REF_RE` in `patterns.py`, and `tests/test_kong.py` + new pattern /
  render test cases.
- Kong notes in `SKILL.md` edge cases, `AGENTS.md` schema / endpoints /
  recipe / failure modes, and the README coverage table.

### Fixed

- Version-entry truncation no longer splits a markdown link mid-`[…](…)`
  (the renderer cuts before an unclosed `[` instead).

## [1.0.0] - 2026-10-08

### Added

- Canonical skills.sh repo layout: `SKILL.md` at repo root, `AGENTS.md` for
  the full reference, `metadata.json` for skills.sh indexers, `LICENSE`
  (MIT), and `CHANGELOG.md`.
- `## When to Use` and `## When Not to Use` sections in `SKILL.md`.
- `## Data Sources` table summarising the four signals and their windows.
- `## Common Edge Cases` section collecting the pitfalls the agent must
  know before running the fetcher.
- `## Output Contract` documenting the JSON schema and report shape.
- `src/gateway_ecosystem_report/` Python package with the fetcher and
  renderer, replacing the loose `scripts/*.py` files.
- `tests/` directory with unit tests for the parsers and the data schema.
- `examples/` directory with a sample run output and fixture data.
- `README.md` with the install badge, install command, and a Quickstart.

### Changed

- Skill name in frontmatter is now `gateway-ecosystem-report` (was the same
  in the previous draft; this is the canonical form).
- Description is now a single ~60-char trigger sentence; long detail lives
  in `AGENTS.md`.
- `metadata.version` is now `"1.0.0"` and is the first indexed release.
- `fetch_data.py` is now `python3 -m gateway_ecosystem_report`; the CLI
  argument shape is unchanged.

### Fixed

- API7 blog parser now reads the `list` key (current schema) and falls back
  to `articles` (legacy schema) instead of failing when the next.js export
  key changes.
- APISIX plugin extractor now scans both `### Plugins` in `CHANGELOG.md`
  and the body of the latest GitHub release so a new plugin is never missed
  when it lands in either channel.
- Higress plugin extractor now correctly filters out the `release-automation`
  bot when its commit message has no plugin scope; it would previously
  inflate counts with `(release-automation)` rows.

## [0.1.0] - 2026-10-08

### Added

- Initial prototype: `SKILL.md`, `scripts/fetch_data.py`,
  `scripts/render_report.py`, and the first generated report.
- Window default of 14 days; CLI args `--days` and `--date`.
- Output as Chinese Markdown with 4 sections.
