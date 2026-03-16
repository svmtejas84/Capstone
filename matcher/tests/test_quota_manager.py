from matcher.quota_manager import quota_from_cedge


def test_quota_from_cedge_has_floor() -> None:
	assert quota_from_cedge(999.0) >= 1
	assert quota_from_cedge(0.0) >= 1

