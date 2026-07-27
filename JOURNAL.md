# PathReview Journal

## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/52

**Issue title:** Add a `contribution_streak` field to the GitHub analysis (longest consecutive days of commits)

**Tier:** [ ] Tier 1  [x] Tier 2  [ ] Tier 3

**Problem summary:**
`GitHubTool` (in `agent/tools/github_tool.py`) currently fetches static repo metadata — stars, forks, language, README presence — for a single repository via the REST API. It has no notion of a user's activity *over time*. The issue asks for a new field, `contribution_streak`, that reports the longest run of consecutive days on which the user made at least one commit, computed from their GitHub contribution history. A successful fix adds a method that pulls the user's daily commit activity (the REST events/commits endpoints only cover ~90 days, so this likely needs the GraphQL `contributionsCollection` calendar for full history), walks the resulting day-by-day activity to find the longest consecutive streak, and surfaces that number alongside the existing repo metadata so the review agent can use it as a portfolio signal.

**"Is this right for me?" reasoning:**
- Tier 2 fits: it touches one existing, well-scoped file (`github_tool.py`) but requires understanding a second GitHub API surface (GraphQL contributions calendar vs. the REST endpoints already used), which is the "cross-module understanding" the tier label calls out.
- Scope is bounded — one new field/method, no schema or API contract changes elsewhere that I could find.
- Estimated 4–6 hours matches a single-week (Week 8) implementation slot, with Week 9 left for polish/PR review.
- No blocking dependencies: the tool has no existing tests to conflict with, and a token-optional pattern (`api_token`) is already established for authenticated GitHub calls.

**Branch name:** `feat/52-contribution-streak`

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [ ] Issue added to cohort ledger — *skipped per your instruction, do this yourself*

## Week 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/ddzhang04/pathreview/commit/5fa32965917e980c9ab4e79f62f8ffc2e64bebb7

**Reproduction summary:**
Issue #52 is a feature gap, so I reproduced it with a failing test rather than by
triggering a fault. `tests/unit/test_github_tool.py` mocks the GitHub REST calls
`GitHubTool` makes and asserts that `execute()` returns a `contribution_streak` key. It
fails with `Got keys: ['description', 'fork_count', 'has_readme', 'homepage',
'last_commit_date', 'name', 'open_issues_count', 'primary_language', 'star_count',
'topics']`, confirming the tool returns only static, repo-scoped metadata and nothing
describing user activity over time. Two control tests in the same file pass, which proves
the failure is a real missing field and not a broken fixture. I also confirmed empirically
that the API needed to fix this behaves differently from the one already in use: an
unauthenticated POST to `api.github.com/graphql` returns `403`, while the REST call the
tool makes today returns `200`.

**PLAN.md link:** https://github.com/ddzhang04/pathreview/blob/feat/52-contribution-streak/PLAN.md

**Walkthrough video (recommended):** Not recorded.

**Blockers or open questions:**
- The issue title says "consecutive days of commits" but the field name is
  `contribution_streak`, and GitHub's calendar reports all contribution types together.
  I chose total daily contributions to match the field name and the familiar green-squares
  metric. I plan to flag this in the PR so the maintainer can redirect me.
- GraphQL requires a token, so `contribution_streak` will be `None` for unauthenticated
  runs while every existing field keeps working. I want to confirm the maintainer prefers
  that over making the tool require a token.
- Request cost scales at one query per year of account history. Unsure whether maintainers
  would rather cache the streak on the profile than recompute it per call.
- The pre-commit mypy hook already fails on `github_tool.py:135` before my change, and the
  file is not black-formatted, so staging it triggers a ~40-line reformat. I need to
  decide in Week 9 between a one-line type fix or a separate formatting commit. I am
  leaning toward the one-line fix to avoid conflicting with upstream.
