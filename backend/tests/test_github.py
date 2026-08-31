import json

from app.routers.webhooks import _verify_signature
from app.services.github import GithubError, parse_pr_url


def test_parse_pr_url():
    ref = parse_pr_url("https://github.com/harbor-labs/checkout-api/pull/1842")
    assert ref.owner == "harbor-labs"
    assert ref.repo == "checkout-api"
    assert ref.number == 1842
    assert ref.slug == "harbor-labs/checkout-api"


def test_parse_pr_url_rejects_other_hosts():
    try:
        parse_pr_url("https://evil.example/github.com/harbor-labs/checkout-api/pull/1")
        assert False, "should have failed"
    except GithubError:
        pass


def test_webhook_signature_roundtrip():
    import hashlib
    import hmac

    from fastapi import HTTPException

    body = json.dumps({"ok": True}).encode()
    secret = "topsecret"
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    _verify_signature(secret, body, "sha256=" + digest)
    try:
        _verify_signature(secret, body, "sha256=deadbeef")
        assert False, "should have failed"
    except HTTPException as exc:
        assert exc.status_code == 401
