from pathlib import Path


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in {"ok", "degraded"}


def test_create_review_from_diff_and_poll(client):
    diff = (Path(__file__).parent / "fixtures" / "sample.diff").read_text()
    created = client.post("/reviews", json={"diff": diff, "title": "local fixture", "heuristics_only": True})
    assert created.status_code == 202
    review_id = created.json()["id"]
    detail = client.get(f"/reviews/{review_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["status"] in {"completed", "failed", "running", "queued"}
    if body["status"] == "completed":
        assert body["finding_count"] >= 1
        assert any(item["category"] == "security" for item in body["findings"])
        assert any(item["fix_suggestion"] for item in body["findings"])
        assert any(item["test_stub"] for item in body["findings"])


def test_create_review_from_github_url(client):
    created = client.post(
        "/reviews",
        json={"pr_url": "https://github.com/harbor-labs/checkout-api/pull/1842", "heuristics_only": True},
    )
    assert created.status_code == 202
    assert created.json()["repo"] == "harbor-labs/checkout-api"
    detail = client.get(f"/reviews/{created.json()['id']}").json()
    assert detail["status"] == "completed"
    assert detail["finding_count"] >= 1


def test_webhook_opens_pull_request(client):
    created = client.post(
        "/webhooks/github",
        content=b'{"action":"opened","pull_request":{"number":1842,"html_url":"https://github.com/harbor-labs/checkout-api/pull/1842","title":"hook","user":{"login":"sara-chen"},"head":{"sha":"abc"},"base":{"ref":"main"}},"repository":{"full_name":"harbor-labs/checkout-api"}}',
        headers={"X-GitHub-Event": "pull_request"},
    )
    assert created.status_code == 200
    review_id = created.json()["queued"]
    detail = client.get(f"/reviews/{review_id}").json()
    assert detail["source"] == "webhook"
    assert detail["status"] == "completed"
    assert detail["finding_count"] >= 1


def test_rejects_empty_payload(client):
    response = client.post("/reviews", json={})
    assert response.status_code == 400


def test_list_and_stats(client):
    listing = client.get("/reviews")
    assert listing.status_code == 200
    stats = client.get("/reviews/stats")
    assert stats.status_code == 200
    assert "cache_hits" in stats.json()
