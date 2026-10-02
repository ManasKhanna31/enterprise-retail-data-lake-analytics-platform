"""Redis cache adapter with deterministic keys and TTL."""
import json
import redis
def cached_store_sales(redis_url: str, store_id: int, loader, ttl_seconds: int = 300):
    client = redis.from_url(redis_url); key = f"retail:sales:store:{store_id}"
    cached = client.get(key)
    if cached: return json.loads(cached)
    value = loader(store_id); client.setex(key, ttl_seconds, json.dumps(value)); return value
