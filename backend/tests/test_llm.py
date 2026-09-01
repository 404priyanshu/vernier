from app.config import Settings
from app.services.llm import parse_findings_payload


def test_parse_findings_payload_filters_junk():
    payload = """
    {
      "findings": [
        {"category": "security", "severity": "critical", "title": "XSS", "file_path": "a.tsx", "start_line": 3},
        {"title": "missing file"},
        "nope"
      ]
    }
    """
    findings = parse_findings_payload(payload)
    assert len(findings) == 1
    assert findings[0]["category"] == "security"
    assert findings[0]["start_line"] == 3


def test_parse_empty_object():
    assert parse_findings_payload("{}") == []


def test_featherless_key_selects_provider():
    settings = Settings(
        featherless_api_key="test-key",
        xai_api_key="",
        openai_api_key="",
        llm_base_url="",
        llm_model="",
    )
    assert settings.llm_api_key == "test-key"
    assert settings.resolved_llm_base_url == "https://api.featherless.ai/v1"
    assert settings.resolved_llm_model == "Qwen/Qwen2.5-Coder-32B-Instruct"
