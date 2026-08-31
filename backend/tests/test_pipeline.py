from pathlib import Path

from app.models import Review
from app.services.diff import flatten_hunks, parse_unified_diff
from app.services.pipeline import analyze_hunks_cached, run_review


def test_pipeline_finds_sql_injection_and_caches_second_run(db_session, ports):
    diff = (Path(__file__).parent / "fixtures" / "sample.diff").read_text()
    review = Review(source="raw_diff", title="fixture", raw_diff=diff, status="queued")
    db_session.add(review)
    db_session.commit()

    result = run_review(db_session, review.id, ports, heuristics_only=False)
    assert result.status == "completed"
    titles = [finding.title for finding in result.findings]
    assert any("SQL" in title for title in titles)
    assert any("pickle" in title.lower() for title in titles)
    assert result.cache_misses >= 1
    assert ports.llm.calls == 1
    first_batches = result.batch_count
    assert first_batches >= 1

    review_two = Review(source="raw_diff", title="fixture-2", raw_diff=diff, status="queued")
    db_session.add(review_two)
    db_session.commit()
    second = run_review(db_session, review_two.id, ports, heuristics_only=False)
    assert second.cache_hits >= 1
    assert second.cache_misses == 0
    assert ports.llm.calls == 1
    assert any(finding.cached for finding in second.findings if finding.source == "llm")


def test_heuristics_only_skips_model(db_session, ports):
    diff = (Path(__file__).parent / "fixtures" / "sample.diff").read_text()
    review = Review(source="raw_diff", title="local", raw_diff=diff, status="queued")
    db_session.add(review)
    db_session.commit()
    before = ports.llm.calls
    result = run_review(db_session, review.id, ports, heuristics_only=True)
    assert result.status == "completed"
    assert ports.llm.calls == before
    assert result.batch_count == 0
    assert all(finding.source == "heuristic" for finding in result.findings)


def test_analyze_hunks_cached_batches(ports):
    diff = (Path(__file__).parent / "fixtures" / "sample.diff").read_text()
    hunks = flatten_hunks(parse_unified_diff(diff))
    ports.settings.batch_max_chars = 80  # type: ignore[misc]
    findings, hits, misses, batches = analyze_hunks_cached(hunks, ports)
    assert misses >= 1
    assert hits == 0
    assert batches >= 1
    assert findings
