def is_stable_assignment(assignment: dict[str, str]) -> bool:
	return all(bool(v) for v in assignment.values())

