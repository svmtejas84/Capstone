from router.stake_audit import create_audit, verify_audit


def test_create_and_verify_audit() -> None:
	stake_hash, _ = create_audit([(13.0, 77.5), (13.1, 77.6)], "seed-1")
	result = verify_audit(stake_hash)
	assert result["valid"] is True


def test_verify_audit_missing() -> None:
	assert verify_audit("no-such-hash")["valid"] is False

