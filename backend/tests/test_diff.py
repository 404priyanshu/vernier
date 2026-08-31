from pathlib import Path

from app.services.diff import flatten_hunks, github_files_to_diff, parse_unified_diff

SAMPLE = (Path(__file__).parent / "fixtures" / "sample.diff").read_text()


def test_parse_extracts_files_and_added_lines():
    files = parse_unified_diff(SAMPLE)
    paths = [item.path for item in files]
    assert paths == [
        "src/db/queries.py",
        "src/auth/session.py",
        "src/api/orders.py",
        "src/config.py",
    ]
    queries = files[0].hunks[0]
    assert "SELECT * FROM orders" in queries.added_text
    assert queries.new_line_span[0] == 12


def test_empty_diff():
    assert parse_unified_diff("") == []
    assert parse_unified_diff("   \n") == []


def test_github_files_to_diff_roundtrip():
    rebuilt = github_files_to_diff(
        [
            {
                "filename": "app.py",
                "patch": "@@ -1,2 +1,3 @@\n def x():\n+    return 1\n     pass",
            }
        ]
    )
    files = parse_unified_diff(rebuilt)
    assert files[0].path == "app.py"
    assert "return 1" in files[0].hunks[0].added_text
    assert flatten_hunks(files)[0].file_path == "app.py"
