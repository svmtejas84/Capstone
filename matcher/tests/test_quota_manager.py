from matcher.quota_manager import quota_from_cedge, quotas_from_route_cedge


def test_quota_from_cedge_has_floor() -> None:
	assert quota_from_cedge(999.0) >= 1
	assert quota_from_cedge(0.0) >= 1


def test_quotas_from_route_cedge_scales_by_concentration() -> None:
	quotas = quotas_from_route_cedge({"a": 8.0, "b": 20.0}, scale=40.0)
	assert quotas["a"] > quotas["b"]

