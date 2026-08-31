def test_github_ping(client):
    response = client.post("/api/webhooks/github", content=b"{}", headers={"X-GitHub-Event": "ping"})
    assert response.status_code == 200
    assert response.json()["pong"] is True


def test_github_ignores_other_events(client):
    response = client.post("/api/webhooks/github", content=b"{}", headers={"X-GitHub-Event": "issues"})
    assert response.json()["ignored"] is True
