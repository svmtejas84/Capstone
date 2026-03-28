from matcher.gale_shapley import batch_match


def test_batch_match_assigns_all_commuters() -> None:
	commuters = ["u1", "u2", "u3", "u4"]
	routes = ["a", "b"]
	assigned = batch_match(commuters, routes)
	assert set(assigned.keys()) == set(commuters)
	assert set(assigned.values()).issubset(set(routes))


def test_batch_match_respects_capacity_and_segment_preference() -> None:
	commuters = ["u1", "u2", "u3"]
	routes = ["a", "b"]

	assigned = batch_match(
		commuters,
		routes,
		commuter_preferences={
			"u1": ["a", "b"],
			"u2": ["a", "b"],
			"u3": ["a", "b"],
		},
		segment_preferences={
			"a": ["u2", "u1", "u3"],
			"b": ["u3", "u1", "u2"],
		},
		segment_capacities={"a": 1, "b": 1},
	)

	# Route a can host one commuter and should keep its top-ranked proposer.
	assert assigned["u2"] == "a"
	assert set(assigned.values()).issubset(set(routes))


def test_batch_match_fallback_assigns_when_iterations_cap_hit() -> None:
	commuters = ["u1", "u2", "u3"]
	routes = ["a", "b"]

	assigned = batch_match(
		commuters,
		routes,
		commuter_preferences={
			"u1": ["a"],
			"u2": ["a"],
			"u3": ["a"],
		},
		segment_preferences={"a": ["u1", "u2", "u3"], "b": ["u1", "u2", "u3"]},
		segment_capacities={"a": 1, "b": 1},
		route_distances={
			"u2": {"a": 12.0, "b": 3.0},
			"u3": {"a": 11.0, "b": 2.5},
		},
		max_iterations=1,
	)

	assert set(assigned.keys()) == set(commuters)
	assert assigned["u2"] == "b"
	assert assigned["u3"] == "b"

