IR_MODE = {
	"jogger": 2.75,
	"cyclist": 1.80,
	"car": 0.65,
}

CABIN_PENALTY_FACTOR = 1.41


def get_ir(mode: str) -> float:
	base = IR_MODE.get(mode, IR_MODE["cyclist"])
	if mode == "car":
		return base * CABIN_PENALTY_FACTOR
	return base

