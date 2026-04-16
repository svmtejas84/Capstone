from matcher.equilibrium_checker import is_stable_assignment


def test_is_stable_assignment_true_when_all_assigned() -> None:
	assert is_stable_assignment({"u1": "a", "u2": "b"}) is True


def test_is_stable_assignment_false_when_missing_route() -> None:
	assert is_stable_assignment({"u1": ""}) is False

