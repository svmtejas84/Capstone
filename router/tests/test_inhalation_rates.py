from router.inhalation_rates import CABIN_PENALTY_FACTOR, IR_MODE, get_ir


def test_get_ir_for_car_includes_penalty() -> None:
	assert get_ir("car") == IR_MODE["car"] * CABIN_PENALTY_FACTOR


def test_get_ir_for_jogger_uses_base() -> None:
	assert get_ir("jogger") == IR_MODE["jogger"]

