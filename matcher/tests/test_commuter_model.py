from matcher.commuter_model import Commuter


def test_commuter_model_fields() -> None:
	c = Commuter(id="u1", mode="jogger", id_min=2.0)
	assert c.id == "u1"
	assert c.mode == "jogger"

