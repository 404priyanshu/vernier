from __future__ import annotations

import re
from dataclasses import dataclass

import httpx

from app.services.diff import github_files_to_diff

PR_URL = re.compile(
    r"https?://(?:www\.)?github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+)/pull/(?P<number>\d+)",
    re.IGNORECASE,
)


class GithubError(ValueError):
    pass


@dataclass(frozen=True)
class PullRequestRef:
    owner: str
    repo: str
    number: int

    @property
    def slug(self) -> str:
        return f"{self.owner}/{self.repo}"

    @property
    def url(self) -> str:
        return f"https://github.com/{self.owner}/{self.repo}/pull/{self.number}"


@dataclass
class PullRequestPayload:
    ref: PullRequestRef
    title: str
    author: str | None
    head_sha: str | None
    base_ref: str | None
    diff: str
    file_count: int


def parse_pr_url(url: str) -> PullRequestRef:
    match = PR_URL.search(url.strip())
    if not match:
        raise GithubError("Expected a GitHub pull request URL such as https://github.com/org/repo/pull/12")
    return PullRequestRef(
        owner=match.group("owner"),
        repo=match.group("repo"),
        number=int(match.group("number")),
    )


class GithubClient:
    def __init__(self, token: str = "", api_url: str = "https://api.github.com") -> None:
        self.token = token
        self.api_url = api_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "vernier-reviewer",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def fetch_pull_request(self, ref: PullRequestRef) -> PullRequestPayload:
        with httpx.Client(timeout=30.0, headers=self._headers()) as client:
            meta_resp = client.get(f"{self.api_url}/repos/{ref.owner}/{ref.repo}/pulls/{ref.number}")
            if meta_resp.status_code == 404:
                raise GithubError(f"Pull request {ref.slug}#{ref.number} was not found. If the repo is private, set GITHUB_TOKEN.")
            if meta_resp.status_code == 403:
                raise GithubError("GitHub rate-limited the request. Set GITHUB_TOKEN to raise the limit.")
            meta_resp.raise_for_status()
            meta = meta_resp.json()

            files: list[dict] = []
            page = 1
            while page <= 10:
                files_resp = client.get(
                    f"{self.api_url}/repos/{ref.owner}/{ref.repo}/pulls/{ref.number}/files",
                    params={"per_page": 100, "page": page},
                )
                files_resp.raise_for_status()
                batch = files_resp.json()
                files.extend(batch)
                if len(batch) < 100:
                    break
                page += 1

        user = meta.get("user") or {}
        head = meta.get("head") or {}
        base = meta.get("base") or {}
        return PullRequestPayload(
            ref=ref,
            title=meta.get("title") or f"{ref.slug}#{ref.number}",
            author=user.get("login"),
            head_sha=head.get("sha"),
            base_ref=base.get("ref"),
            diff=github_files_to_diff(files),
            file_count=len(files),
        )
