from matcher.commuter_model import Commuter, build_preference_list


def test_commuter_model_fields() -> None:
	c = Commuter(id="u1", mode="jogger", id_min=2.0)
	assert c.id == "u1"
	assert c.mode == "jogger"


def test_build_preference_list_prioritizes_lower_dose_for_jogger() -> None:
	c = Commuter(id="u1", mode="jogger", id_min=2.0, distance_tolerance_m=6000.0)
	routes = ["a", "b"]
	prefs = build_preference_list(
		c,
		routes,
		route_dose={"a": 30.0, "b": 10.0},
		route_distance_m={"a": 1200.0, "b": 2400.0},
	)
	assert prefs[0] == "b"

