from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict
import time

try:
    import redis
except Exception:  # pragma: no cover - optional dependency
    redis = None


@dataclass
class LinearScaler:
    a: float = 1.0
    b: float = 0.0
    version: str = "init"
    last_updated: float = 0.0
    min_samples: int = 10

    def apply(self, x: float) -> float:
        return float(self.a * x + self.b)


class ScalerStore:
    """In-memory cache of per-zone linear scalers with optional Redis backing.

    Intended usage:
      store = ScalerStore(redis_client=redis_client)
      store.set_scaler(zone_id, a, b, version="v1")
      y_scaled = store.apply(zone_id, y_raw)
    """

    def __init__(self, redis_client: Optional[object] = None, redis_prefix: str = "scaler:") -> None:
        self._cache: Dict[str, LinearScaler] = {}
        self._redis = redis_client
        self._prefix = redis_prefix

    def get(self, zone_id: str) -> LinearScaler:
        if zone_id in self._cache:
            return self._cache[zone_id]
        # fallback to global
        return self._cache.get("__global__", LinearScaler())

    def set_scaler(self, zone_id: str, a: float, b: float, version: str = "v1", min_samples: int = 10) -> None:
        s = LinearScaler(a=float(a), b=float(b), version=str(version), last_updated=time.time(), min_samples=int(min_samples))
        self._cache[zone_id] = s
        if self._redis is not None and redis is not None:
            try:
                key = f"{self._prefix}{zone_id}"
                self._redis.hset(key, mapping={"a": s.a, "b": s.b, "version": s.version, "last_updated": s.last_updated, "min_samples": s.min_samples})
            except Exception:
                pass

    def apply(self, zone_id: str, x: float) -> float:
        s = self.get(zone_id)
        return s.apply(x)

    def refresh_from_redis(self) -> None:
        if self._redis is None or redis is None:
            return
        try:
            keys = self._redis.keys(f"{self._prefix}*")
            for k in keys:
                zid = k.decode().replace(self._prefix, "") if isinstance(k, bytes) else k.replace(self._prefix, "")
                data = self._redis.hgetall(k)
                if not data:
                    continue
                try:
                    a = float(data.get(b"a", data.get("a", 1.0)))
                    b = float(data.get(b"b", data.get("b", 0.0)))
                    version = (data.get(b"version") or data.get("version") or b"").decode() if isinstance(data.get(b"version"), bytes) else str(data.get("version") or "")
                    min_samples = int(data.get(b"min_samples", data.get("min_samples", 10)))
                except Exception:
                    continue
                self._cache[zid] = LinearScaler(a=a, b=b, version=version, last_updated=time.time(), min_samples=min_samples)
        except Exception:
            return


__all__ = ["ScalerStore", "LinearScaler"]
