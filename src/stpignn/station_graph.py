"""Explicit station-subset graph for tractable observed-only comparisons."""
import numpy as np
import torch


def directed_knn_graph(coordinates_utm_m: np.ndarray, neighbours: int):
    xy = np.asarray(coordinates_utm_m, dtype=np.float64)
    if xy.ndim != 2 or xy.shape[1] != 2 or len(xy) < 2:
        raise ValueError("Expected projected station coordinates [N,2]")
    if not 1 <= neighbours < len(xy):
        raise ValueError("Neighbour count must be between 1 and N-1")
    distance = np.linalg.norm(xy[:, None, :] - xy[None, :, :], axis=-1)
    np.fill_diagonal(distance, np.inf)
    closest = np.argsort(distance, axis=1)[:, :neighbours]
    source = np.repeat(np.arange(len(xy)), neighbours)
    destination = closest.reshape(-1)
    edge_index = torch.as_tensor(np.stack([source, destination]), dtype=torch.long)
    edge_length_m = torch.as_tensor(distance[source, destination, None], dtype=torch.float32)
    return edge_index, edge_length_m
