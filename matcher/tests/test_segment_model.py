from matcher.commuter_model import Commuter
from matcher.segment_model import Segment, build_preference_list


def test_segment_model_fields() -> None:
	s = Segment(id="corridor_a", cedge_mean=12.0, capacity=3)
	assert s.capacity == 3


def test_build_preference_list_prioritizes_vulnerable_commuter() -> None:
	segment = Segment(id="corridor_a", cedge_mean=12.0, capacity=2)
	commuters = [
		Commuter(id="car_user", mode="car", id_min=3.0),
		Commuter(id="jogger_user", mode="jogger", id_min=2.0),
	]
	prefs = build_preference_list(segment, commuters)
	assert prefs[0] == "jogger_user"

