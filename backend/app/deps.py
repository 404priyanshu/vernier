from functools import lru_cache

from app.config import Settings, get_settings
from app.services.cache import CacheBackend, MemoryCache, RedisCache
from app.services.github import GithubClient
from app.services.llm import LLMAnalyzer
from app.services.pipeline import PipelinePorts


@lru_cache
def get_cache() -> CacheBackend:
    settings = get_settings()
    try:
        cache = RedisCache(settings.redis_url)
        cache.client.ping()
        return cache
    except Exception:
        return MemoryCache()


@lru_cache
def get_ports() -> PipelinePorts:
    settings = get_settings()
    return PipelinePorts(
        cache=get_cache(),
        llm=LLMAnalyzer(
            api_key=settings.llm_api_key,
            base_url=settings.resolved_llm_base_url,
            model=settings.resolved_llm_model,
        ),
        github=GithubClient(token=settings.github_token, api_url=settings.github_api_url),
        settings=settings,
    )


def ports_from_settings(settings: Settings, cache: CacheBackend | None = None) -> PipelinePorts:
    return PipelinePorts(
        cache=cache or MemoryCache(),
        llm=LLMAnalyzer(
            api_key=settings.llm_api_key,
            base_url=settings.resolved_llm_base_url,
            model=settings.resolved_llm_model,
        ),
        github=GithubClient(token=settings.github_token, api_url=settings.github_api_url),
        settings=settings,
    )
