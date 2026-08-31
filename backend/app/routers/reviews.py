from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.database import get_db
from app.deps import get_cache, get_ports
from app.models import Finding, Review
from app.schemas import ReviewDetail, ReviewSummary, ScanRequest, StatsOut
from app.services.cache import STATS_HITS, STATS_MISSES, CacheBackend
from app.services.github import GithubError, parse_pr_url
from app.services.pipeline import PipelinePorts, run_review

router = APIRouter(prefix="/reviews", tags=["reviews"])


def _summary(review: Review) -> ReviewSummary:
    return ReviewSummary(
        id=review.id,
        source=review.source,
        status=review.status,
        repo=review.repo,
        pr_number=review.pr_number,
        pr_url=review.pr_url,
        title=review.title,
        author=review.author,
        summary=review.summary,
        error=review.error,
        model=review.model,
        prompt_version=review.prompt_version,
        cache_hits=review.cache_hits,
        cache_misses=review.cache_misses,
        batch_count=review.batch_count,
        hunk_count=review.hunk_count,
        file_count=review.file_count,
        finding_count=len(review.findings) if review.findings is not None else 0,
        created_at=review.created_at,
        completed_at=review.completed_at,
    )


@router.get("", response_model=list[ReviewSummary])
def list_reviews(db: Session = Depends(get_db)) -> list[ReviewSummary]:
    reviews = db.scalars(
        select(Review).options(selectinload(Review.findings)).order_by(Review.created_at.desc())
    ).all()
    return [_summary(review) for review in reviews]


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db), cache: CacheBackend = Depends(get_cache)) -> StatsOut:
    settings = get_settings()
    review_count = db.scalar(select(func.count()).select_from(Review)) or 0
    completed = db.scalar(select(func.count()).select_from(Review).where(Review.status == "completed")) or 0
    findings = db.scalar(select(func.count()).select_from(Finding)) or 0
    hits = cache.get_json(STATS_HITS)
    misses = cache.get_json(STATS_MISSES)
    if hits is None and hasattr(cache, "counters"):
        hits = cache.counters.get(STATS_HITS, 0)
        misses = cache.counters.get(STATS_MISSES, 0)
    try:
        hits_n = int(hits or 0)
        misses_n = int(misses or 0)
    except (TypeError, ValueError):
        hits_n, misses_n = 0, 0
    return StatsOut(
        reviews=review_count,
        completed=completed,
        findings=findings,
        cache_hits=hits_n,
        cache_misses=misses_n,
        llm_configured=bool(settings.llm_api_key),
        model=settings.llm_model,
        prompt_version=settings.prompt_version,
    )


@router.get("/{review_id}", response_model=ReviewDetail)
def get_review(review_id: str, db: Session = Depends(get_db)) -> ReviewDetail:
    review = db.scalar(select(Review).options(selectinload(Review.findings)).where(Review.id == review_id))
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    detail = ReviewDetail.model_validate(review)
    detail.finding_count = len(review.findings)
    return detail


@router.post("", response_model=ReviewSummary, status_code=200)
def create_review(
    payload: ScanRequest,
    db: Session = Depends(get_db),
    ports: PipelinePorts = Depends(get_ports),
) -> ReviewSummary:
    if not payload.pr_url and not payload.diff:
        raise HTTPException(status_code=400, detail="Provide pr_url or diff.")

    title = payload.title or "Untitled review"
    repo = None
    pr_number = None
    pr_url = payload.pr_url
    source = "raw_diff"
    if payload.pr_url:
        try:
            ref = parse_pr_url(payload.pr_url)
        except GithubError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        source = "github_pr"
        repo = ref.slug
        pr_number = ref.number
        pr_url = ref.url
        title = payload.title or f"{ref.slug}#{ref.number}"

    review = Review(
        source=source,
        status="queued",
        repo=repo,
        pr_number=pr_number,
        pr_url=pr_url,
        title=title,
        raw_diff=payload.diff,
        prompt_version=get_settings().prompt_version,
        model=ports.llm.model,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    try:
        run_review(db, review.id, ports, heuristics_only=payload.heuristics_only)
    except Exception:
        pass
    loaded = db.scalar(select(Review).options(selectinload(Review.findings)).where(Review.id == review.id))
    if loaded is None:
        raise HTTPException(status_code=500, detail="Review was not saved")
    return _summary(loaded)
