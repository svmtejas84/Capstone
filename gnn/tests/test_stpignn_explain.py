from gnn.stpignn_explain import explain_route_edges_with_integrated_gradients


def test_stpignn_explain_empty_route_is_unavailable() -> None:
	explanation = explain_route_edges_with_integrated_gradients([])

	assert explanation.available is False
	assert explanation.method == "captum.integrated_gradients"
	assert explanation.feature_attributions == {}
	assert explanation.reason == "route has no edges"
