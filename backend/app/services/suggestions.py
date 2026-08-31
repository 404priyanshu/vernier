from __future__ import annotations

from app.services.heuristics import HeuristicHit

FIXES: dict[str, str] = {
    "sql_fstring": """from sqlalchemy import text

stmt = text("SELECT * FROM orders WHERE user_id = :user_id AND status = 'active'")
cursor.execute(stmt, {"user_id": user_id})
""",
    "sql_concat": """stmt = "SELECT * FROM orders WHERE user_id = %s AND status = 'active'"
cursor.execute(stmt, (user_id,))
""",
    "pickle_loads": """import json

session = json.loads(raw)
""",
    "yaml_unsafe_load": """config = yaml.safe_load(payload)
""",
    "shell_true": """subprocess.run(["git", "status"], check=True)
""",
    "os_system": """subprocess.run(["ls", path], check=True)
""",
    "eval_exec": """# Parse the value with json.loads or ast.literal_eval instead of eval.
data = json.loads(raw)
""",
    "innerhtml": """node.textContent = userText
""",
    "hardcoded_secret": """import os

SECRET_KEY = os.environ["SECRET_KEY"]
""",
    "md5_password": """import hashlib

digest = hashlib.sha256(value.encode()).hexdigest()  # still not a password hash
# For passwords use argon2 or bcrypt, never a fast checksum.
""",
    "insecure_random": """import secrets

token = secrets.token_urlsafe(32)
""",
    "debug_true": """DEBUG = False
""",
    "cors_star": """allow_origins=["https://app.example.com"]
""",
    "jwt_skip_verify": """payload = jwt.decode(token, key, algorithms=["HS256"])
""",
    "n_plus_one": """items = db.query(Item).filter(Item.order_id.in_(order_ids)).all()
""",
    "blocking_in_async": """await asyncio.sleep(delay)
# or: async with httpx.AsyncClient() as client: await client.get(url)
""",
    "nested_loops": """index = {item.id: item for item in items}
for key in keys:
    match = index.get(key)
""",
    "mutable_default": """def handle(items: list[str] | None = None):
    items = list(items or [])
""",
    "bare_except": """except (ValueError, OSError) as exc:
    log.warning("failed", exc_info=exc)
""",
    "is_none_eq": """if value is None:
    return
""",
    "todo_fixme": """# Resolve the FIXME before merge, or file a tracked issue and remove the marker.
""",
}

TESTS: dict[str, str] = {
    "sql_fstring": '''def test_get_user_orders_rejects_injection(client):
    response = client.get("/orders", params={"user_id": "1' OR '1'='1"})
    assert response.status_code in {400, 404}
    assert "DROP" not in (response.text or "")
''',
    "sql_concat": '''def test_orders_query_uses_parameters(monkeypatch):
    seen = {}
    def fake_execute(sql, params=None):
        seen["sql"] = sql
        seen["params"] = params
    monkeypatch.setattr(cursor, "execute", fake_execute)
    get_user_orders("u-1")
    assert "%s" in seen["sql"] or ":user_id" in seen["sql"]
    assert "u-1" not in seen["sql"]
''',
    "pickle_loads": '''def test_session_restore_rejects_pickle(tmp_path):
    payload = b"cos\\nsystem\\n(S'echo pwned'\\ntR."
    with pytest.raises((ValueError, json.JSONDecodeError, TypeError)):
        restore_session(payload)
''',
    "yaml_unsafe_load": '''def test_config_load_does_not_construct_objects():
    raw = "!!python/object/apply:os.system ['echo pwned']"
    with pytest.raises(Exception):
        load_config(raw)
''',
    "shell_true": '''def test_run_git_does_not_use_shell(monkeypatch):
    seen = {}
    def fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        seen["shell"] = kwargs.get("shell", False)
        return types.SimpleNamespace(returncode=0)
    monkeypatch.setattr(subprocess, "run", fake_run)
    status()
    assert seen["shell"] is False
    assert isinstance(seen["cmd"], list)
''',
    "eval_exec": '''def test_parse_payload_does_not_eval():
    with pytest.raises((json.JSONDecodeError, ValueError)):
        parse_payload("__import__('os').system('echo pwned')")
''',
    "innerhtml": '''it("writes user text as text content", () => {
  const node = document.createElement("div");
  renderUser(node, "<img src=x onerror=alert(1)>");
  expect(node.innerHTML).not.toMatch(/onerror/);
  expect(node.textContent).toContain("<img");
});
''',
    "hardcoded_secret": '''def test_secret_comes_from_environment(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "from-env")
    import importlib
    mod = importlib.reload(config)
    assert mod.SECRET_KEY == "from-env"
''',
    "n_plus_one": '''def test_items_are_fetched_in_one_query(db):
    with assert_max_queries(db, 2):
        load_orders_with_items(order_ids)
''',
    "mutable_default": '''def test_handler_does_not_leak_list_state():
    handle(items=["a"])
    assert handle() == []
''',
    "blocking_in_async": '''@pytest.mark.asyncio
async def test_fetch_does_not_block_event_loop(monkeypatch):
    async def fake_get(url):
        return httpx.Response(200, json={})
    monkeypatch.setattr(client, "get", fake_get)
    await fetch_remote()
''',
}


def suggest_fix(hit: HeuristicHit) -> str:
    return FIXES.get(hit.detector_id, f"# Address {hit.title.lower()} in {hit.file_path}.")


def suggest_test(hit: HeuristicHit) -> str:
    return TESTS.get(
        hit.detector_id,
        f'def test_{hit.detector_id}():\n    """Regression for {hit.title} in {hit.file_path}."""\n    raise AssertionError("write the failing case first")\n',
    )
