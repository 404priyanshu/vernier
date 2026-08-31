from __future__ import annotations

import hashlib
import hmac
import json

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import get_ports
from app.models import Review
from app.services.pipeline import PipelinePorts, run_review

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def _verify_signature(secret: str, body: bytes, signature: str | None) -> None:
    if not secret:
        return
    if not signature or not signature.startswith("sha256="):
        raise HTTPException(status_code=401, detail="Missing GitHub signature")
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Invalid GitHub signature")


@router.post("/github")
async def github_webhook(
    request: Request,
    db: Session = Depends(get_db),
    ports: PipelinePorts = Depends(get_ports),
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
) -> dict:
    body = await request.body()
    settings = get_settings()
    _verify_signature(settings.github_webhook_secret, body, x_hub_signature_256)
    if x_github_event not in {"pull_request", "ping"}:
        return {"ignored": True, "event": x_github_event}
    if x_github_event == "ping":
        return {"pong": True}

    payload = json.loads(body.decode("utf-8"))
    action = payload.get("action")
    if action not in {"opened", "synchronize", "reopened"}:
        return {"ignored": True, "action": action}

    pr = payload.get("pull_request") or {}
    repo = payload.get("repository") or {}
    full_name = repo.get("full_name")
    number = pr.get("number")
    html_url = pr.get("html_url")
    if not full_name or not number or not html_url:
        raise HTTPException(status_code=400, detail="Webhook payload missing pull request fields")

    review = Review(
        source="webhook",
        status="queued",
        repo=full_name,
        pr_number=int(number),
        pr_url=html_url,
        title=pr.get("title") or f"{full_name}#{number}",
        author=(pr.get("user") or {}).get("login"),
        head_sha=(pr.get("head") or {}).get("sha"),
        base_ref=(pr.get("base") or {}).get("ref"),
        prompt_version=settings.prompt_version,
        model=ports.llm.model,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    try:
        run_review(db, review.id, ports)
    except Exception:
        pass
    return {"queued": review.id}
