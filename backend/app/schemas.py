from datetime import datetime

from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    pr_url: str | None = None
    diff: str | None = None
    title: str | None = None
    heuristics_only: bool = False


class FindingOut(BaseModel):
    id: str
    category: str
    severity: str
    title: str
    description: str
    file_path: str
    start_line: int | None
    end_line: int | None
    snippet: str | None
    confidence: float
    source: str
    detector_id: str | None
    fix_suggestion: str | None
    test_stub: str | None
    cached: bool

    model_config = {"from_attributes": True}


class ReviewSummary(BaseModel):
    id: str
    source: str
    status: str
    repo: str | None
    pr_number: int | None
    pr_url: str | None
    title: str
    author: str | None
    summary: str | None
    error: str | None
    model: str | None
    prompt_version: str
    cache_hits: int
    cache_misses: int
    batch_count: int
    hunk_count: int
    file_count: int
    finding_count: int = 0
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class ReviewDetail(ReviewSummary):
    findings: list[FindingOut] = Field(default_factory=list)
    head_sha: str | None = None
    base_ref: str | None = None


class StatsOut(BaseModel):
    reviews: int
    completed: int
    findings: int
    cache_hits: int
    cache_misses: int
    llm_configured: bool
    model: str
    prompt_version: str
