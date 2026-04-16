from gnn.graph_builder import build_demo_graph


def test_build_demo_graph_non_empty() -> None:
	g = build_demo_graph()
	assert g.number_of_nodes() > 0
	assert g.number_of_edges() > 0
	u, v = next(iter(g.edges()))
	assert "length_m" in g[u][v]
	assert "bearing_deg" in g[u][v]
	assert "building_density" in g[u][v]

