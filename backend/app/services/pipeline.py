from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.config import Settings
from app.models import Finding, Review
from app.services.batching import pack_batches
from app.services.cache import STATS_HITS, STATS_MISSES, CacheBackend, hunk_cache_key
from app.services.diff import flatten_hunks, parse_unified_diff
from app.services.github import GithubClient, GithubError, parse_pr_url
from app.services.heuristics import SEVERITY_RANK, HeuristicHit, scan_hunks
from app.services.llm import LLMAnalyzer
from app.services.suggestions import suggest_fix, suggest_test


@dataclass
class PipelinePorts:
    cache: CacheBackend
    llm: LLMAnalyzer
    github: GithubClient
    settings: Settings


def enqueue_sources(review: Review, ports: PipelinePorts) -> None:
    if review.source in {"github_pr", "webhook"} and review.pr_url:
        ref = parse_pr_url(review.pr_url)
        payload = ports.github.fetch_pull_request(ref)
        review.repo = payload.ref.slug
        review.pr_number = payload.ref.number
        review.pr_url = payload.ref.url
        review.title = payload.title
        review.author = payload.author
        review.head_sha = payload.head_sha
        review.base_ref = payload.base_ref
        review.raw_diff = payload.diff
        review.file_count = payload.file_count
    elif review.raw_diff:
        files = parse_unified_diff(review.raw_diff)
        review.file_count = len(files)
    else:
        raise GithubError("Provide a GitHub pull request URL or a unified diff.")


def run_review(db: Session, review_id: str, ports: PipelinePorts, heuristics_only: bool = False) -> Review:
    review = db.get(Review, review_id)
    if review is None:
        raise KeyError(review_id)
    review.status = "running"
    review.model = ports.llm.model
    review.prompt_version = ports.settings.prompt_version
    db.commit()
    try:
        enqueue_sources(review, ports)
        files = parse_unified_diff(review.raw_diff or "")
        hunks = flatten_hunks(files)
        review.hunk_count = len(hunks)
        review.file_count = review.file_count or len(files)

        heuristic_hits = scan_hunks(hunks)
        llm_findings, hits, misses, batches = ([], 0, 0, 0)
        if not heuristics_only:
            llm_findings, hits, misses, batches = analyze_hunks_cached(hunks, ports)

        review.cache_hits = hits
        review.cache_misses = misses
        review.batch_count = batches
        merged = merge_findings(heuristic_hits, llm_findings)
        persist_findings(db, review, merged)
        review.summary = summarize(merged)
        review.status = "completed"
        review.completed_at = datetime.now(UTC)
        review.error = None
        db.commit()
        db.refresh(review)
        return review
    except Exception as exc:
        review.status = "failed"
        review.error = str(exc)
        review.completed_at = datetime.now(UTC)
        db.commit()
        raise


def analyze_hunks_cached(
    hunks: list,
    ports: PipelinePorts,
) -> tuple[list[dict[str, Any]], int, int, int]:
    settings = ports.settings
    model = ports.llm.model
    hits = 0
    misses = 0
    cached_findings: list[dict[str, Any]] = []
    pending = []

    for hunk in hunks:
        if not hunk.added_text.strip():
            continue
        key = hunk_cache_key(settings.prompt_version, model, hunk.normalize())
        cached = ports.cache.get_json(key)
        if cached is not None:
            hits += 1
            for item in cached:
                tagged = dict(item)
                tagged["_cached"] = True
                cached_findings.append(tagged)
        else:
            misses += 1
            pending.append((key, hunk))

    batches = pack_batches([hunk for _, hunk in pending], max_chars=settings.batch_max_chars)
    fresh: list[dict[str, Any]] = []
    if pending and ports.llm.enabled:
        key_by_path: dict[str, list[str]] = {}
        for key, hunk in pending:
            key_by_path.setdefault(hunk.file_path, []).append(key)
        for batch in batches:
            produced = ports.llm.analyze_batch(batch)
            by_file: dict[str, list[dict[str, Any]]] = {}
            for item in produced:
                by_file.setdefault(item["file_path"], []).append(item)
                fresh.append(item)
            for hunk in batch:
                key = hunk_cache_key(settings.prompt_version, model, hunk.normalize())
                payload = by_file.get(hunk.file_path, [])
                ports.cache.set_json(key, payload, settings.cache_ttl_seconds)

    ports.cache.incr(STATS_HITS, hits or 0)
    ports.cache.incr(STATS_MISSES, misses or 0)
    return cached_findings + fresh, hits, misses, len(batches)


def merge_findings(heuristics: list[HeuristicHit], llm_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[tuple] = set()

    def mark(file_path: str, category: str, line: int | None, title: str) -> tuple:
        bucket = (line // 8) if line else 0
        return (file_path, category, bucket, title.lower()[:48])

    for item in llm_items:
        key = mark(item["file_path"], item["category"], item.get("start_line"), item["title"])
        seen.add(key)
        cached_flag = bool(item.pop("_cached", False))
        merged.append(
            {
                **item,
                "source": "llm",
                "detector_id": None,
                "cached": cached_flag,
            }
        )

    for hit in heuristics:
        key = mark(hit.file_path, hit.category, hit.start_line, hit.title)
        if key in seen:
            for item in merged:
                if mark(item["file_path"], item["category"], item.get("start_line"), item["title"]) == key:
                    item["source"] = "merged"
                    if not item.get("fix_suggestion"):
                        item["fix_suggestion"] = suggest_fix(hit)
                    if not item.get("test_stub"):
                        item["test_stub"] = suggest_test(hit)
                    break
            continue
        seen.add(key)
        merged.append(
            {
                "category": hit.category,
                "severity": hit.severity,
                "title": hit.title,
                "description": hit.description,
                "file_path": hit.file_path,
                "start_line": hit.start_line,
                "end_line": hit.end_line,
                "snippet": hit.snippet,
                "confidence": hit.confidence,
                "source": "heuristic",
                "detector_id": hit.detector_id,
                "fix_suggestion": suggest_fix(hit),
                "test_stub": suggest_test(hit),
                "cached": False,
            }
        )
    return merged


def persist_findings(db: Session, review: Review, items: list[dict[str, Any]]) -> None:
    review.findings.clear()
    db.flush()
    for item in items:
        severity = item["severity"]
        db.add(
            Finding(
                review_id=review.id,
                category=item["category"],
                severity=severity,
                severity_rank=SEVERITY_RANK.get(severity, 50),
                title=item["title"],
                description=item["description"],
                file_path=item["file_path"],
                start_line=item.get("start_line"),
                end_line=item.get("end_line"),
                snippet=item.get("snippet"),
                confidence=item.get("confidence") or 0.7,
                source=item.get("source") or "heuristic",
                detector_id=item.get("detector_id"),
                fix_suggestion=item.get("fix_suggestion"),
                test_stub=item.get("test_stub"),
                cached=bool(item.get("cached")),
            )
        )


def summarize(items: list[dict[str, Any]]) -> str:
    if not items:
        return "No findings. The diff did not trip heuristic detectors or the model."
    counts: dict[str, int] = {}
    for item in items:
        counts[item["category"]] = counts.get(item["category"], 0) + 1
    parts = [f"{count} {name}" for name, count in sorted(counts.items())]
    critical = sum(1 for item in items if item["severity"] in {"critical", "high"})
    lead = f"{len(items)} finding" if len(items) == 1 else f"{len(items)} findings"
    return f"{lead}: {', '.join(parts)}. {critical} rated high or critical."
