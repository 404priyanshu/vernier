from app.services.batching import pack_batches
from app.services.diff import parse_unified_diff


def test_pack_respects_char_budget():
    hunks = []
    for index in range(6):
        path = f"file_{index}.py"
        diff = f"""diff --git a/{path} b/{path}
--- a/{path}
+++ b/{path}
@@ -1,1 +1,2 @@
 def f():
+    value = '{index}' * 80
"""
        hunks.extend(parse_unified_diff(diff)[0].hunks)
    batches = pack_batches(hunks, max_chars=120)
    assert len(batches) > 1
    assert sum(len(batch) for batch in batches) == 6


def test_skips_hunks_without_additions():
    diff = """diff --git a/a.py b/a.py
--- a/a.py
+++ b/a.py
@@ -1,2 +1,1 @@
-removed
 context
"""
    hunks = parse_unified_diff(diff)[0].hunks
    assert pack_batches(hunks, max_chars=8000) == []
