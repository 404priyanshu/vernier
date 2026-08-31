from app.services.cache import MemoryCache, hunk_cache_key


def test_hunk_cache_key_is_stable():
    first = hunk_cache_key("review-v1", "grok-4.6", "a.py\nadd:x")
    second = hunk_cache_key("review-v1", "grok-4.6", "a.py\nadd:x")
    third = hunk_cache_key("review-v1", "grok-4.6", "a.py\nadd:y")
    assert first == second
    assert first != third
    assert first.startswith("vernier:llm:")


def test_memory_cache_roundtrip():
    cache = MemoryCache()
    cache.set_json("k", [{"title": "x"}], ttl=10)
    assert cache.get_json("k") == [{"title": "x"}]
    assert cache.get_json("missing") is None
    assert cache.incr("c") == 1
    assert cache.incr("c", 4) == 5
