from app.services.routing.router import score_route


def test_mode_weights_are_distinct() -> None:
    jogger, _ = score_route("jogger")
    car, _ = score_route("car")
    assert jogger > car
