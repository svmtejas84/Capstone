from __future__ import annotations

from math import atan2, degrees, hypot, sin, radians

import networkx as nx
import numpy as np

from gnn.angular_diffusion import directional_diffusion_weight
from gnn.plume_physics import (
	dispersion_sigmas,
	effective_wind_speed,
	gaussian_plume,
	urban_canyon_correction,
)


class PIGNN:
	def __init__(
		self,
		sigma_deg: float = 35.0,
		downwind_cone_deg: float = 75.0,
		message_alpha: float = 0.35,
		temporal_damping: float = 0.6,
	) -> None:
		self.sigma_deg = sigma_deg
		self.downwind_cone_deg = downwind_cone_deg
		self.message_alpha = message_alpha
		self.temporal_damping = max(0.05, min(1.0, temporal_damping))

	def _wind_state(self, wind_u: np.ndarray, wind_v: np.ndarray) -> tuple[float, float]:
		u_mean = float(np.mean(wind_u))
		v_mean = float(np.mean(wind_v))
		wind_speed = max(0.2, hypot(u_mean, v_mean))
		wind_dir = (degrees(atan2(v_mean, u_mean)) + 360.0) % 360.0
		return wind_speed, wind_dir

	def forward(
		self,
		graph: nx.DiGraph,
		edge_values: dict[tuple[int, int], float],
		wind_u: np.ndarray,
		wind_v: np.ndarray,
		steps: int = 2,
	) -> dict[tuple[int, int], float]:
		wind_speed, wind_dir = self._wind_state(wind_u, wind_v)
		state = dict(edge_values)

		def incoming_edge_mean(target_node: int, prev_state: dict[tuple[int, int], float]) -> float:
			incoming = [prev_state[(p, target_node)] for p in graph.predecessors(target_node) if (p, target_node) in prev_state]
			if not incoming:
				return 0.0
			indegree = max(1, graph.in_degree(target_node))
			return float(sum(incoming) / len(incoming)) / indegree

		for _ in range(max(1, steps)):
			prev_state = state
			next_state: dict[tuple[int, int], float] = {}

			for edge, base in prev_state.items():
				u, v = edge
				attrs = graph[u][v]
				length_m = float(attrs.get("length_m", 100.0))
				bearing_deg = float(attrs.get("bearing_deg", 0.0))
				building_density = float(attrs.get("building_density", 0.5))

				diff_weight = directional_diffusion_weight(
					edge_bearing_deg=bearing_deg,
					wind_dir_deg=wind_dir,
					sigma_deg=self.sigma_deg,
					cone_deg=self.downwind_cone_deg,
				)

				delta_theta = abs(((bearing_deg - wind_dir + 180.0) % 360.0) - 180.0)
				y_crosswind_m = abs(sin(radians(delta_theta)) * length_m)
				sigma_y, sigma_z = dispersion_sigmas(length_m)

				eff_wind = effective_wind_speed(wind_speed, building_density)
				plume_term = gaussian_plume(
					q=max(0.1, base),
					x_downwind_m=length_m,
					y_crosswind_m=y_crosswind_m,
					wind_speed=eff_wind,
					sigma_y=sigma_y,
					sigma_z=sigma_z,
				)

				# Multi-hop message from upstream incoming edges into node u.
				upstream_signal = incoming_edge_mean(u, prev_state)
				pred_raw = base + diff_weight * plume_term + self.message_alpha * upstream_signal * diff_weight
				pred_raw = urban_canyon_correction(pred_raw, building_density=building_density, wind_speed=eff_wind)

				# Temporal damping prevents unrealistically abrupt jumps over many propagation steps.
				damped = (1.0 - self.temporal_damping) * base + self.temporal_damping * pred_raw
				next_state[edge] = max(0.0, min(500.0, float(damped)))

			state = next_state

		return state

