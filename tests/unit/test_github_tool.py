"""Tests for github_tool.py

Reproduction for issue #52 — GitHubTool exposes no `contribution_streak`.
https://github.com/ascherj/pathreview/issues/52

`test_execute_returns_contribution_streak` is the reproduction case and is
EXPECTED TO FAIL until #52 is implemented. The two tests above it pass today
and exist to prove the failure is a genuine missing field rather than a broken
fixture: the same mocked response that satisfies them is missing only the one
key the issue asks for.
"""

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from agent.tools.github_tool import GitHubTool

# Minimal shape of GET /repos/{owner}/{repo}, trimmed to the keys the tool reads.
FAKE_REPO_JSON = {
    "name": "pathreview",
    "description": "AI-powered portfolio review",
    "language": "Python",
    "stargazers_count": 42,
    "forks_count": 7,
    "open_issues_count": 3,
    "pushed_at": "2026-07-20T12:00:00Z",
    "topics": ["ai", "fastapi"],
    "homepage": "https://example.com",
}


class FakeResponse:
    """Stand-in for httpx.Response covering only what GitHubTool touches."""

    def __init__(self, json_data: dict, status_code: int = 200) -> None:
        self._json = json_data
        self.status_code = status_code

    def json(self) -> dict:
        return self._json

    def raise_for_status(self) -> None:
        return None


@pytest.mark.unit
class TestGitHubToolContributionStreak:
    """Reproduce the missing `contribution_streak` field from issue #52."""

    @pytest.fixture
    def tool(self) -> GitHubTool:
        return GitHubTool()

    @pytest.fixture
    def mocked_github(self) -> Iterator[tuple[MagicMock, MagicMock]]:
        """Patch the HTTP calls GitHubTool makes so tests never hit the network."""
        with (
            patch("agent.tools.github_tool.httpx.get") as mock_get,
            patch("agent.tools.github_tool.httpx.head") as mock_head,
        ):
            mock_get.return_value = FakeResponse(FAKE_REPO_JSON)
            mock_head.return_value = FakeResponse({}, status_code=200)
            yield mock_get, mock_head

    def test_execute_succeeds_with_existing_metadata(
        self, tool: GitHubTool, mocked_github: tuple[MagicMock, MagicMock]
    ) -> None:
        """Control: the tool works today and returns its documented fields."""
        result = tool.execute({"github_username": "ddzhang04", "repo_name": "pathreview"})

        assert result.success is True
        assert result.data["star_count"] == 42
        assert result.data["primary_language"] == "Python"
        assert result.data["has_readme"] is True

    def test_execute_returns_only_static_repo_metadata(
        self, tool: GitHubTool, mocked_github: tuple[MagicMock, MagicMock]
    ) -> None:
        """Control: pins the current field set, so the gap below is unambiguous.

        Every key here describes the *repository* at a point in time. None of
        them describe the *user's activity over time*, which is what #52 wants.
        """
        result = tool.execute({"github_username": "ddzhang04", "repo_name": "pathreview"})

        assert set(result.data.keys()) == {
            "name",
            "description",
            "primary_language",
            "star_count",
            "fork_count",
            "open_issues_count",
            "last_commit_date",
            "has_readme",
            "topics",
            "homepage",
        }

    def test_execute_returns_contribution_streak(
        self, tool: GitHubTool, mocked_github: tuple[MagicMock, MagicMock]
    ) -> None:
        """REPRODUCTION (issue #52): expected to fail until the fix lands.

        Expected: result.data carries a `contribution_streak` integer — the
        longest run of consecutive days the user committed on.
        Actual:   KeyError, the tool never computes or returns the field.
        """
        result = tool.execute({"github_username": "ddzhang04", "repo_name": "pathreview"})

        assert result.success is True
        assert "contribution_streak" in result.data, (
            "issue #52: GitHubTool returns no contribution_streak. "
            f"Got keys: {sorted(result.data)}"
        )
        assert isinstance(result.data["contribution_streak"], int)
        assert result.data["contribution_streak"] >= 0
