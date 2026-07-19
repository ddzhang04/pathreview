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
