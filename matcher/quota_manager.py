def quota_from_cedge(cedge_mean: float, scale: float = 10.0) -> int:
	if cedge_mean <= 0:
		return int(scale)
	return max(1, int(scale / cedge_mean))

