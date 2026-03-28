from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Commuter(BaseModel):
	id: str
	mode: Literal["jogger", "cyclist", "car"]
	id_min: float = Field(default=2.0, gt=0)
	distance_tolerance_m: float = Field(default=8000.0, gt=0)


MODE_ALPHA: dict[str, float] = {
	"jogger": 0.75,
	"cyclist": 0.60,
	"car": 0.35,
}


def build_preference_list(
	commuter: Commuter,
	route_ids: list[str],
	route_dose: dict[str, float],
	route_distance_m: dict[str, float],
	mode_alpha: dict[str, float] | None = None,
) -> list[str]:
	"""Rank routes by weighted toxicity dose and distance tolerance ratio."""
	if not route_ids:
		return []

	alpha_map = mode_alpha or MODE_ALPHA
	alpha = alpha_map.get(commuter.mode, 0.5)

	available_doses = [max(0.0, route_dose.get(rid, float("inf"))) for rid in route_ids]
	finite_doses = [v for v in available_doses if v != float("inf")]
	max_dose = max(finite_doses) if finite_doses else 1.0
	if max_dose <= 0:
		max_dose = 1.0

	ranked: list[tuple[float, int, str]] = []
	for idx, rid in enumerate(route_ids):
		dose = route_dose.get(rid, float("inf"))
		norm_dose = (dose / max_dose) if dose != float("inf") else float("inf")
		distance_ratio = route_distance_m.get(rid, float("inf")) / commuter.distance_tolerance_m
		score = alpha * norm_dose + (1.0 - alpha) * distance_ratio
		ranked.append((score, idx, rid))

	ranked.sort(key=lambda x: (x[0], x[1]))
	return [rid for _, _, rid in ranked]

