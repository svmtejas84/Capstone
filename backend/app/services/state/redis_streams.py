import json
from typing import Any

from redis import Redis

from app.core.config import settings


def get_client() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


def publish_grid_snapshot(stream_name: str, payload: dict[str, Any]) -> str:
    client = get_client()
    return client.xadd(stream_name, {"data": json.dumps(payload)})
