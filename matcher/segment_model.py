from __future__ import annotations

from pydantic import BaseModel, Field

from matcher.commuter_model import Commuter


class Segment(BaseModel):
	id: str
	cedge_mean: float
	capacity: int = Field(ge=1)
	vulnerability_preference: dict[str, float] = Field(
		default_factory=lambda: {
			"jogger": 3.0,
			"cyclist": 2.0,
			"two_wheeler": 1.0,
			"car": 1.0,  # legacy alias retained for compatibility
		}
	)


def build_preference_list(
	segment: Segment,
	commuters: list[Commuter],
	*,
	congestion_penalty: float = 0.0,
) -> list[str]:
	"""Rank commuters by vulnerability priority for this segment."""
	den = 1.0 + max(0.0, congestion_penalty)
	ranked: list[tuple[float, str]] = []
	for commuter in commuters:
		mode_weight = segment.vulnerability_preference.get(commuter.mode, 1.0)
		physiology_weight = 1.0 / commuter.id_min
		score = (mode_weight + physiology_weight) / den
		ranked.append((score, commuter.id))

	ranked.sort(key=lambda x: (-x[0], x[1]))
	return [cid for _, cid in ranked]

