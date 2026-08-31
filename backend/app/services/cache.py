from __future__ import annotations

import hashlib
import json
from typing import Any, Protocol


class CacheBackend(Protocol):
    def get_json(self, key: str) -> Any | None: ...

    def set_json(self, key: str, value: Any, ttl: int) -> None: ...

    def incr(self, key: str, amount: int = 1) -> int: ...


class MemoryCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}
        self.counters: dict[str, int] = {}

    def get_json(self, key: str) -> Any | None:
        return self.store.get(key)

    def set_json(self, key: str, value: Any, ttl: int) -> None:
        self.store[key] = value

    def incr(self, key: str, amount: int = 1) -> int:
        self.counters[key] = self.counters.get(key, 0) + amount
        return self.counters[key]


class RedisCache:
    def __init__(self, url: str) -> None:
        import redis

        self.client = redis.from_url(url, decode_responses=True)

    def get_json(self, key: str) -> Any | None:
        raw = self.client.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    def set_json(self, key: str, value: Any, ttl: int) -> None:
        self.client.setex(key, ttl, json.dumps(value))

    def incr(self, key: str, amount: int = 1) -> int:
        return int(self.client.incrby(key, amount))


def hunk_cache_key(prompt_version: str, model: str, hunk_normalized: str) -> str:
    digest = hashlib.sha256(
        json.dumps(
            {
                "prompt_version": prompt_version,
                "model": model,
                "hunk": hunk_normalized,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return f"vernier:llm:{digest}"


STATS_HITS = "vernier:stats:hits"
STATS_MISSES = "vernier:stats:misses"
