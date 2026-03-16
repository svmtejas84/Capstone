from matcher.gale_shapley import batch_match


def test_batch_match_assigns_all_commuters() -> None:
	commuters = ["u1", "u2", "u3", "u4"]
	routes = ["a", "b"]
	assigned = batch_match(commuters, routes)
	assert set(assigned.keys()) == set(commuters)
	assert set(assigned.values()).issubset(set(routes))

