def predict_wake_polygon() -> dict[str, object]:
	return {
		"type": "Feature",
		"geometry": {
			"type": "Polygon",
			"coordinates": [[[77.58, 13.03], [77.60, 13.03], [77.61, 13.05], [77.58, 13.03]]],
		},
		"properties": {"label": "simulated-wake", "horizon_minutes": 10},
	}

