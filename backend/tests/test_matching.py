from app.services.matching.gale_shapley import stable_match


def test_stable_match_assigns_routes() -> None:
    commuters = ["u1", "u2"]
    routes = ["r1", "r2"]
    prefs = {
        "u1": ["r1", "r2"],
        "u2": ["r1", "r2"],
    }
    result = stable_match(commuters, routes, prefs)
    assert len(result) >= 1
