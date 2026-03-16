from matcher.segment_model import Segment


def test_segment_model_fields() -> None:
	s = Segment(id="corridor_a", cedge_mean=12.0, capacity=3)
	assert s.capacity == 3

