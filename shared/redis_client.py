from __future__ import annotations

from typing import Any

from redis import Redis
from redis.exceptions import RedisError

from shared.config import get_settings


class RedisStore:
	def __init__(self) -> None:
		self._settings = get_settings()
		self._client: Redis | None = None

	def connect(self) -> None:
		try:
			self._client = Redis.from_url(self._settings.redis_url, decode_responses=True)
			self._client.ping()
		except RedisError:
			self._client = None

	@property
	def client(self) -> Redis | None:
		return self._client

	def xadd(self, stream: str, fields: dict[str, Any], maxlen: int = 30) -> None:
		if self._client is None:
			return
		self._client.xadd(stream, fields, maxlen=maxlen, approximate=True)

	def hset_json(self, key: str, field: str, value: str) -> None:
		if self._client is None:
			return
		self._client.hset(key, field, value)

	def hset(self, key: str, field: str, value: str) -> None:
		if self._client is None:
			return
		self._client.hset(key, field, value)

	def hget(self, key: str, field: str) -> str | None:
		if self._client is None:
			return None
		return self._client.hget(key, field)

	def hgetall(self, key: str) -> dict[str, str]:
		if self._client is None:
			return {}
		return self._client.hgetall(key)

