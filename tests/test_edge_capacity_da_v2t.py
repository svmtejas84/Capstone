"""Frozen critical correctness gate for the additive v2t allocator."""
from itertools import product

import pytest
from matcher.edge_capacity_da import allocate_shared_edges


def run(ids, prefs, paths, edge_caps, route_caps=None, ranks=None):
    return allocate_shared_edges(ids, prefs, paths,
        route_caps or {r: 1 for r in paths}, edge_caps,
        ranks or {r: ids for r in paths})


def test_competition_and_unassigned_without_fallback():
    a = run(["a", "b"], {"a": ["r"], "b": ["r"]}, {"r": [(1, 2)]}, {(1, 2): 1})
    assert a == {"a": "r", "b": None}


def test_shared_bottleneck_and_release_then_reproposal():
    paths = {"r1": [(1, 2), (2, 3)], "r2": [(1, 2), (2, 4)],
             "alt": [(1, 5), (5, 4)]}
    caps = {e: 1 for path in paths.values() for e in path}
    a = run(["a", "b"], {"a": ["r1"], "b": ["r2", "alt"]}, paths, caps)
    assert a == {"a": "r1", "b": "alt"}


def test_displacement_releases_all_edges_atomically():
    paths = {"r": [(1, 2), (2, 3)], "alt": [(4, 5)]}
    caps = {(1, 2): 1, (2, 3): 1, (4, 5): 1}
    a = run(["a", "b"], {"a": ["r", "alt"], "b": ["r"]}, paths, caps,
            ranks={"r": ["b", "a"], "alt": ["a", "b"]})
    assert a == {"a": "alt", "b": "r"}


def test_multiple_independent_routes():
    paths = {"r": [(1, 2)], "s": [(3, 4)]}
    a = run(["a", "b"], {"a": ["r"], "b": ["s"]}, paths,
            {(1, 2): 1, (3, 4): 1})
    assert a == {"a": "r", "b": "s"}


def test_zero_capacity_and_excess_demand():
    a = run(["a", "b"], {"a": ["r"], "b": ["r"]},
            {"r": [(1, 2)]}, {(1, 2): 0})
    assert a == {"a": None, "b": None}


def test_multiple_overlapping_bundles_feasible():
    paths = {"a": [(1, 2), (2, 3)], "b": [(1, 2), (2, 4)],
             "c": [(5, 2), (2, 3)]}
    caps = {e: 1 for p in paths.values() for e in p}
    a = run(["u", "v", "w"], {"u": ["a"], "v": ["b"], "w": ["c"]}, paths, caps)
    for e, cap in caps.items():
        assert sum(e in paths[r] for r in a.values() if r) <= cap


def test_missing_candidate_is_unassigned():
    assert run(["a"], {"a": ["unknown"]}, {}, {}) == {"a": None}
    assert run(["a"], {"a": []}, {}, {}) == {"a": None}


@pytest.mark.parametrize("paths,caps", [
    ({"r": []}, {}),
    ({"r": [(1, 2), (3, 4)]}, {(1, 2): 1, (3, 4): 1}),
    ({"r": [(1, 2)]}, {}),
])
def test_invalid_routes_rejected(paths, caps):
    with pytest.raises(ValueError):
        run(["a"], {"a": ["r"]}, paths, caps)


def test_repeated_commuter_ids_rejected():
    with pytest.raises(ValueError):
        run(["a", "a"], {"a": ["r"]}, {"r": [(1, 2)]}, {(1, 2): 1})


def test_identical_preferences_deterministic():
    args = (["b", "a"], {"a": ["r"], "b": ["r"]},
            {"r": [(1, 2)]}, {(1, 2): 1})
    assert run(*args, ranks={"r": []}) == run(*args, ranks={"r": []}) == {"a": "r", "b": None}


def test_exhaustive_reference_feasibility():
    paths = {"r": [(1, 2), (2, 3)], "s": [(1, 2), (2, 4)],
             "t": [(5, 6)]}
    caps = {e: 1 for p in paths.values() for e in p}
    ids = ["a", "b", "c"]
    a = run(ids, {c: list(paths) for c in ids}, paths, caps,
            route_caps={r: 1 for r in paths})
    feasible = []
    for choices in product([None, *paths], repeat=len(ids)):
        if all(sum(e in paths[r] for r in choices if r) <= caps[e] for e in caps):
            feasible.append(choices)
    assert tuple(a[c] for c in ids) in feasible


def test_directed_edges_are_distinct_resources():
    paths = {"forward": [(1, 2)], "backward": [(2, 1)]}
    a = run(["a", "b"], {"a": ["forward"], "b": ["backward"]}, paths,
            {(1, 2): 1, (2, 1): 1})
    assert a == {"a": "forward", "b": "backward"}


def test_disconnected_od_yields_no_candidate_path():
    import networkx as nx
    from router.api.routes import _candidate_paths
    g = nx.MultiDiGraph()
    g.add_node(1, x=0., y=0.)
    g.add_node(2, x=1., y=0.)
    assert _candidate_paths(g, 1, 2, mode="cyclist", k=3) == []
