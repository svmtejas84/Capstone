IR_MODE = {
	"jogger": 2.75,
	"cyclist": 1.80,
	"two_wheeler": 0.65,
}

# Legacy references retained for backward compatibility and comparison studies.
LEGACY_CAR_IR = 0.65
LEGACY_CAR_CABIN_PENALTY_FACTOR = 1.41

MODE_ALIASES = {
	"two-wheeler": "two_wheeler",
}


def get_ir(mode: str) -> float:
	mode_key = MODE_ALIASES.get(mode.lower(), mode.lower())
	if mode_key == "car":
		return LEGACY_CAR_IR * LEGACY_CAR_CABIN_PENALTY_FACTOR
	base = IR_MODE.get(mode_key, IR_MODE["cyclist"])
	return base

