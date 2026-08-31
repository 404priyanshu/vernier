from app.services.diff import Hunk, parse_unified_diff
from app.services.heuristics import scan_hunk, scan_hunks


def _hunk(path: str, added: str, start: int = 1) -> Hunk:
    diff = f"""diff --git a/{path} b/{path}
--- a/{path}
+++ b/{path}
@@ -{start},0 +{start},{len(added.splitlines())} @@
""" + "".join(f"+{line}\n" for line in added.splitlines())
    return parse_unified_diff(diff)[0].hunks[0]


def test_sql_fstring_detected():
    hunk = _hunk(
        "src/db/queries.py",
        "query = f\"SELECT * FROM orders WHERE user_id = '{user_id}'\"\ncursor.execute(query)",
    )
    hits = scan_hunk(hunk)
    assert any(hit.detector_id == "sql_fstring" for hit in hits)
    assert hits[0].category == "security"
    assert hits[0].severity == "critical"


def test_pickle_and_secret_and_debug():
    pickle_hits = scan_hunk(_hunk("src/auth/session.py", "return pickle.loads(raw)"))
    secret_hits = scan_hunk(_hunk("src/config.py", 'SECRET_KEY = "supersecret123456"'))
    debug_hits = scan_hunk(_hunk("src/config.py", "DEBUG = True"))
    assert pickle_hits[0].detector_id == "pickle_loads"
    assert secret_hits[0].detector_id == "hardcoded_secret"
    assert debug_hits[0].detector_id == "debug_true"


def test_innerhtml_skipped_on_python():
    hunk = _hunk("app.py", "node.innerHTML = user")
    assert scan_hunk(hunk) == []


def test_innerhtml_on_tsx():
    hunk = _hunk("Widget.tsx", "return <div dangerouslySetInnerHTML={{__html: html}} />")
    assert any(hit.detector_id == "innerhtml" for hit in scan_hunk(hunk))


def test_jwt_none_algorithm():
    hunk = _hunk("auth.py", "payload = jwt.decode(token, key, algorithms=['none'])")
    assert any(hit.detector_id == "jwt_skip_verify" for hit in scan_hunk(hunk))


def test_scan_hunks_sample_diff():
    from pathlib import Path

    diff = (Path(__file__).parent / "fixtures" / "sample.diff").read_text()
    files = parse_unified_diff(diff)
    hits = scan_hunks([hunk for file in files for hunk in file.hunks])
    detectors = {hit.detector_id for hit in hits}
    assert "sql_fstring" in detectors
    assert "pickle_loads" in detectors
    assert "hardcoded_secret" in detectors
