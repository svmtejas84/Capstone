from __future__ import annotations


def batch_match(commuter_ids: list[str], route_ids: list[str]) -> dict[str, str]:
	if not route_ids:
		return {cid: "" for cid in commuter_ids}
	out: dict[str, str] = {}
	for i, cid in enumerate(commuter_ids):
		out[cid] = route_ids[i % len(route_ids)]
	return out

