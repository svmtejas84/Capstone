from __future__ import annotations


def quota_from_cedge(
	cedge_mean: float,
	*,
	scale: float = 10.0,
	min_quota: int = 1,
	max_quota: int | None = None,
) -> int:
	if cedge_mean <= 0:
		raw = int(scale)
	else:
		raw = int(scale / cedge_mean)

	quota = max(min_quota, raw)
	if max_quota is not None:
		quota = min(quota, max_quota)
	return quota


def quotas_from_route_cedge(
	route_cedge: dict[str, float],
	*,
	scale: float = 10.0,
	min_quota: int = 1,
	max_quota: int | None = None,
) -> dict[str, int]:
	return {
		rid: quota_from_cedge(
			cedge,
			scale=scale,
			min_quota=min_quota,
			max_quota=max_quota,
		)
		for rid, cedge in route_cedge.items()
	}

