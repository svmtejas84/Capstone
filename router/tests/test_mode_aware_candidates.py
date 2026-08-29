import networkx as nx

from matcher.commuter_model import Commuter
from router.api.routes import _build_batch_commuters, _candidate_paths


def test_candidate_paths_trade_exposure_for_distance_by_mode() -> None:
	graph = nx.MultiDiGraph()
	graph.add_nodes_from((node_id, {"x": float(node_id), "y": 0.0}) for node_id in range(1, 5))
	# Path 1→2→4 is longer but less polluted; path 1→3→4 is shorter but dirtier.
	graph.add_edge(1, 2, length=1000.0)
	graph.add_edge(2, 4, length=1000.0)
	graph.add_edge(1, 3, length=600.0)
	graph.add_edge(3, 4, length=600.0)
	toxicity = {(1, 2): 1.0, (2, 4): 1.0, (1, 3): 3.0, (3, 4): 3.0}

	assert _candidate_paths(graph, 1, 4, mode="jogger", k=1, tox_preds=toxicity) == [[1, 2, 4]]
	assert _candidate_paths(graph, 1, 4, mode="car", k=1, tox_preds=toxicity) == [[1, 3, 4]]


def test_explicit_commuter_counts_build_the_requested_cohort() -> None:
	requester = Commuter(id="requester", mode="cyclist")
	cohort = _build_batch_commuters(
		requester,
		{"jogger": 2, "cyclist": 3, "two_wheeler": 1, "car": 4},
	)

	assert len(cohort) == 10
	assert sum(commuter.mode == "cyclist" for commuter in cohort) == 3
	assert _build_batch_commuters(requester) == [requester]
