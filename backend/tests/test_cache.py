from app.services import cache


def test_cache_put_get():
    cache.put("test", "key1", value={"x": 1})
    assert cache.get("test", "key1") == {"x": 1}


def test_cache_miss():
    assert cache.get("test", "missing") is None


def test_cache_invalidate():
    cache.put("test", "k", value=1)
    cache.invalidate("test", "k")
    assert cache.get("test", "k") is None