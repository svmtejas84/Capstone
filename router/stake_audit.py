from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from shared.redis_client import RedisStore

_AUDIT_STORE: dict[str, dict[str, object]] = {}
AUDIT_LOG_KEY = "toxicity:audit_log"


def create_audit(
	route: list[tuple[float, float]],
	env_seed: str,
	store: RedisStore | None = None,
) -> tuple[str, dict[str, object]]:
	ts = datetime.now(timezone.utc).isoformat()
	payload = {"route": route, "env_seed": env_seed, "timestamp": ts}
	raw = json.dumps(payload, sort_keys=True)
	stake_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
	_AUDIT_STORE[stake_hash] = payload
	if store is not None:
		store.hset(AUDIT_LOG_KEY, stake_hash, raw)
	return stake_hash, payload


def verify_audit(stake_hash: str, store: RedisStore | None = None) -> dict[str, object]:
	if store is not None:
		raw = store.hget(AUDIT_LOG_KEY, stake_hash)
		if raw:
			record = json.loads(raw)
			return {"valid": True, **record}

	rec = _AUDIT_STORE.get(stake_hash)
	if rec is None:
		return {"valid": False}
	return {"valid": True, **rec}

