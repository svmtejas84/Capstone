from router.inhalation_rates import (
	IR_MODE,
	LEGACY_CAR_CABIN_PENALTY_FACTOR,
	LEGACY_CAR_IR,
	get_ir,
)


def test_get_ir_for_two_wheeler_uses_primary_mode() -> None:
	assert get_ir("two_wheeler") == IR_MODE["two_wheeler"]


def test_get_ir_for_car_kept_as_legacy_reference() -> None:
	assert get_ir("car") == LEGACY_CAR_IR * LEGACY_CAR_CABIN_PENALTY_FACTOR


def test_get_ir_for_jogger_uses_base() -> None:
	assert get_ir("jogger") == IR_MODE["jogger"]

