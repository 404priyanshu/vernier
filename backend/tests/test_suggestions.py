from app.services.heuristics import HeuristicHit
from app.services.suggestions import suggest_fix, suggest_test


def test_sql_fix_uses_bound_parameters():
    hit = HeuristicHit(
        detector_id="sql_fstring",
        category="security",
        severity="critical",
        title="SQL",
        description="d",
        file_path="q.py",
        start_line=1,
        end_line=1,
        snippet="x",
    )
    fix = suggest_fix(hit)
    test = suggest_test(hit)
    assert ":user_id" in fix or "%s" in fix
    assert "def test_" in test
    assert "OR" in test or "injection" in test
