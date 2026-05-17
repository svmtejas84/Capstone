from gnn.stpignn_explain import explain_route_edges_with_stpignn


def test_stpignn_explain_empty_route_is_unavailable() -> None:
	explanation = explain_route_edges_with_stpignn([])

	assert explanation.available is False
	assert explanation.method == "shap.gradient"
	assert explanation.feature_attributions == {}
	assert explanation.reason == "route has no edges"
