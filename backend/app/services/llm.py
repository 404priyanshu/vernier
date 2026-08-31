from __future__ import annotations

import json
from typing import Any

from app.prompts import SYSTEM_PROMPT, build_user_prompt
from app.services.diff import Hunk


class LLMError(RuntimeError):
    pass


class LLMAnalyzer:
    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self._client = None

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _client_or_none(self):
        if not self.enabled:
            return None
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def analyze_batch(self, hunks: list[Hunk]) -> list[dict[str, Any]]:
        client = self._client_or_none()
        if client is None or not hunks:
            return []
        response = client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(hunks)},
            ],
        )
        content = response.choices[0].message.content or "{}"
        return parse_findings_payload(content)


def parse_findings_payload(content: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise LLMError(f"Model returned invalid JSON: {exc}") from exc
    findings = payload.get("findings", payload if isinstance(payload, list) else [])
    if not isinstance(findings, list):
        return []
    cleaned: list[dict[str, Any]] = []
    for item in findings:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        file_path = str(item.get("file_path") or "").strip()
        if not title or not file_path:
            continue
        cleaned.append(
            {
                "category": _one_of(item.get("category"), {"security", "bug", "performance"}, "bug"),
                "severity": _one_of(
                    item.get("severity"), {"critical", "high", "medium", "low", "info"}, "medium"
                ),
                "title": title[:512],
                "description": str(item.get("description") or title),
                "file_path": file_path[:512],
                "start_line": _as_int(item.get("start_line")),
                "end_line": _as_int(item.get("end_line")),
                "snippet": (item.get("snippet") or None),
                "confidence": _as_float(item.get("confidence"), 0.7),
                "fix_suggestion": item.get("fix_suggestion") or None,
                "test_stub": item.get("test_stub") or None,
            }
        )
    return cleaned


def _one_of(value: Any, allowed: set[str], default: str) -> str:
    text = str(value or "").strip().lower()
    return text if text in allowed else default


def _as_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _as_float(value: Any, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, number))
