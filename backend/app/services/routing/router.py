INHALATION_RATE = {
    "jogger": 2.6,
    "cyclist": 1.9,
    "car": 0.9,
}


def score_route(mode: str) -> tuple[float, int]:
    # Placeholder for W = sum(Cedge * te * IRmode).
    c_edge = [0.8, 1.2, 0.9, 0.7]
    t_edge = [70, 120, 80, 60]
    ir = INHALATION_RATE.get(mode, INHALATION_RATE["car"])
    weight = sum(c * t * ir for c, t in zip(c_edge, t_edge))
    eta = sum(t_edge)
    return float(weight), eta
