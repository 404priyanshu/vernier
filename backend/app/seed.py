from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Finding, Review, new_id
from app.services.heuristics import SEVERITY_RANK

SAMPLE_DIFF = """diff --git a/src/db/queries.py b/src/db/queries.py
index 1111111..2222222 100644
--- a/src/db/queries.py
+++ b/src/db/queries.py
@@ -10,6 +10,9 @@ def get_user_orders(user_id):
     conn = get_conn()
     cursor = conn.cursor()
+    query = f"SELECT * FROM orders WHERE user_id = '{user_id}' AND status = 'active'"
+    cursor.execute(query)
+    return cursor.fetchall()

diff --git a/src/auth/session.py b/src/auth/session.py
index 3333333..4444444 100644
--- a/src/auth/session.py
+++ b/src/auth/session.py
@@ -20,4 +20,6 @@ def restore_session(raw: bytes):
     # TODO: replace the transport format
+    import pickle
+    return pickle.loads(raw)

diff --git a/src/api/orders.py b/src/api/orders.py
index 5555555..6666666 100644
--- a/src/api/orders.py
+++ b/src/api/orders.py
@@ -40,3 +40,8 @@ def load_orders_with_items(order_ids):
     items = []
+    for order_id in order_ids:
+        items.append(db.query(Item).filter(Item.order_id == order_id).all())
+    return items

diff --git a/src/config.py b/src/config.py
index 7777777..8888888 100644
--- a/src/config.py
+++ b/src/config.py
@@ -1,3 +1,5 @@
 import os
+DEBUG = True
+SECRET_KEY = "supersecret123456"
"""

SAMPLE_FINDINGS = [
    {
        "category": "security",
        "severity": "critical",
        "title": "SQL query built with a formatted string",
        "description": "user_id is interpolated into SQL. An attacker can append OR 1=1 or UNION SELECT and read other customers' orders.",
        "file_path": "src/db/queries.py",
        "start_line": 12,
        "end_line": 13,
        "snippet": "query = f\"SELECT * FROM orders WHERE user_id = '{user_id}' AND status = 'active'\"",
        "confidence": 0.94,
        "source": "merged",
        "detector_id": "sql_fstring",
        "fix_suggestion": "from sqlalchemy import text\n\nstmt = text(\"SELECT * FROM orders WHERE user_id = :user_id AND status = 'active'\")\ncursor.execute(stmt, {\"user_id\": user_id})\n",
        "test_stub": "def test_get_user_orders_rejects_injection(client):\n    response = client.get(\"/orders\", params={\"user_id\": \"1' OR '1'='1\"})\n    assert response.status_code in {400, 404}\n",
        "cached": False,
    },
    {
        "category": "security",
        "severity": "critical",
        "title": "Unsafe pickle deserialization",
        "description": "pickle.loads on session bytes is remote code execution if an attacker can write the blob.",
        "file_path": "src/auth/session.py",
        "start_line": 23,
        "end_line": 23,
        "snippet": "return pickle.loads(raw)",
        "confidence": 0.95,
        "source": "heuristic",
        "detector_id": "pickle_loads",
        "fix_suggestion": "import json\n\nsession = json.loads(raw)\n",
        "test_stub": "def test_session_restore_rejects_pickle():\n    with pytest.raises((ValueError, json.JSONDecodeError, TypeError)):\n        restore_session(b\"cos\\nsystem\\n(S'id'\\ntR.\")\n",
        "cached": False,
    },
    {
        "category": "performance",
        "severity": "medium",
        "title": "Query inside a loop",
        "description": "Each order_id issues its own SELECT. Fetch all items with IN (...) or a join instead.",
        "file_path": "src/api/orders.py",
        "start_line": 42,
        "end_line": 43,
        "snippet": "items.append(db.query(Item).filter(Item.order_id == order_id).all())",
        "confidence": 0.7,
        "source": "heuristic",
        "detector_id": "n_plus_one",
        "fix_suggestion": "items = db.query(Item).filter(Item.order_id.in_(order_ids)).all()\n",
        "test_stub": "def test_items_are_fetched_in_one_query(db):\n    with assert_max_queries(db, 2):\n        load_orders_with_items(order_ids)\n",
        "cached": True,
    },
    {
        "category": "security",
        "severity": "high",
        "title": "Hardcoded credential",
        "description": "SECRET_KEY is committed in source. Anyone with repo access can forge sessions.",
        "file_path": "src/config.py",
        "start_line": 4,
        "end_line": 4,
        "snippet": "SECRET_KEY = \"supersecret123456\"",
        "confidence": 0.8,
        "source": "heuristic",
        "detector_id": "hardcoded_secret",
        "fix_suggestion": "import os\n\nSECRET_KEY = os.environ[\"SECRET_KEY\"]\n",
        "test_stub": "def test_secret_comes_from_environment(monkeypatch):\n    monkeypatch.setenv(\"SECRET_KEY\", \"from-env\")\n    assert config.SECRET_KEY == \"from-env\"\n",
        "cached": False,
    },
    {
        "category": "security",
        "severity": "medium",
        "title": "Debug mode enabled",
        "description": "DEBUG = True will leak tracebacks if this module is imported in production.",
        "file_path": "src/config.py",
        "start_line": 3,
        "end_line": 3,
        "snippet": "DEBUG = True",
        "confidence": 0.72,
        "source": "heuristic",
        "detector_id": "debug_true",
        "fix_suggestion": "DEBUG = False\n",
        "test_stub": "def test_debug_is_off():\n    assert config.DEBUG is False\n",
        "cached": False,
    },
]


def seed_if_empty(db: Session) -> None:
    existing = db.scalar(select(Review.id).limit(1))
    if existing:
        return
    now = datetime.now(UTC)
    review = Review(
        id=new_id(),
        source="github_pr",
        status="completed",
        repo="harbor-labs/checkout-api",
        pr_number=1842,
        pr_url="https://github.com/harbor-labs/checkout-api/pull/1842",
        title="Harden order lookup and restore sessions from cache",
        author="sara-chen",
        head_sha="b7c91e2aa1",
        base_ref="main",
        summary="5 findings: 4 security, 1 performance. 3 rated high or critical.",
        model="grok-4.6",
        prompt_version="review-v1",
        cache_hits=1,
        cache_misses=3,
        batch_count=1,
        hunk_count=4,
        file_count=4,
        raw_diff=SAMPLE_DIFF,
        created_at=now,
        completed_at=now,
    )
    db.add(review)
    db.flush()
    for item in SAMPLE_FINDINGS:
        db.add(
            Finding(
                review_id=review.id,
                category=item["category"],
                severity=item["severity"],
                severity_rank=SEVERITY_RANK[item["severity"]],
                title=item["title"],
                description=item["description"],
                file_path=item["file_path"],
                start_line=item["start_line"],
                end_line=item["end_line"],
                snippet=item["snippet"],
                confidence=item["confidence"],
                source=item["source"],
                detector_id=item["detector_id"],
                fix_suggestion=item["fix_suggestion"],
                test_stub=item["test_stub"],
                cached=item["cached"],
            )
        )
    db.commit()
