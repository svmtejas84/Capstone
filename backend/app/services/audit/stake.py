import hashlib
import time


def build_route_stake(mode: str, total_weight: float) -> str:
    raw = f"{mode}:{total_weight:.4f}:{int(time.time())}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
