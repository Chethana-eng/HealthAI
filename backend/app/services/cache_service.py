from cachetools import TTLCache


symptom_cache = TTLCache(
    maxsize=100,
    ttl=300
)


def get_cached_result(key: str):

    return symptom_cache.get(key)


def set_cached_result(key: str, result: dict):

    symptom_cache[key] = result