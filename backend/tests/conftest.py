from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import get_settings
from app.database import Base, SessionLocal, get_db, reset_engine
from app.deps import get_cache, get_ports
from app.main import create_app
from app.services.cache import MemoryCache
from app.services.pipeline import PipelinePorts


class FakeLLM:
    enabled = True
    model = "fake-model"
    calls = 0

    def analyze_batch(self, hunks):
        self.calls += 1
        first = hunks[0]
        return [
            {
                "category": "bug",
                "severity": "low",
                "title": "Model noted a risky addition",
                "description": "Synthetic finding used in tests.",
                "file_path": first.file_path,
                "start_line": first.new_start,
                "end_line": first.new_start,
                "snippet": first.added_text.splitlines()[0] if first.added_text else "",
                "confidence": 0.51,
                "fix_suggestion": "cover with a regression test",
                "test_stub": "def test_synthetic():\n    assert True\n",
            }
        ]


class FakeGithub:
    def fetch_pull_request(self, ref):
        from app.services.github import PullRequestPayload

        diff = (Path(__file__).parent / "fixtures" / "sample.diff").read_text()
        return PullRequestPayload(
            ref=ref,
            title="Harden order lookup",
            author="sara-chen",
            head_sha="abc123",
            base_ref="main",
            diff=diff,
            file_count=4,
        )


@pytest.fixture
def memory_cache() -> MemoryCache:
    return MemoryCache()


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("SEED_ON_STARTUP", "false")
    monkeypatch.setenv("XAI_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()
    get_cache.cache_clear()
    get_ports.cache_clear()
    return get_settings()


@pytest.fixture
def db_session(settings):
    reset_engine("sqlite://")
    # Recreate with StaticPool so the in-memory DB is shared.
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    SessionLocal.configure(bind=engine)
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def ports(settings, memory_cache) -> PipelinePorts:
    return PipelinePorts(
        cache=memory_cache,
        llm=FakeLLM(),
        github=FakeGithub(),
        settings=settings,
    )


@pytest.fixture
def client(db_session, ports):
    app = create_app()

    def override_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_ports] = lambda: ports
    app.dependency_overrides[get_cache] = lambda: ports.cache
    with TestClient(app) as test_client:
        yield test_client
