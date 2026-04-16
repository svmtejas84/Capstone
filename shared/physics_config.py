"""
shared/physics_config.py

Centralized physics constants and configuration for all cities.
Supports multi-city deployments with city-agnostic urban physics.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Literal


# Weight for physics-informed regularization term in composite training loss.
PHYSICS_LOSS_LAMBDA: float = 0.1

# Project root: parent of this shared module directory.
BASE_DIR = Path(__file__).resolve().parent.parent


class StabilityClass(str, Enum):
    """Pasquill-Gifford stability classes A-F based on atmospheric conditions."""

    A = "A"  # Highly unstable (strong convection)
    B = "B"  # Unstable
    C = "C"  # Slightly unstable
    D = "D"  # Neutral
    E = "E"  # Slightly stable
    F = "F"  # Stable (strong inversion)


def get_pasquill_stability(
    wind_speed_ms: float,
    solar_radiation_wm2: float | None = None,
    is_night: bool = False,
) -> StabilityClass:
    """
    Determine Pasquill stability class from wind speed and solar/nocturnal conditions.

    Args:
        wind_speed_ms: Wind speed at 10m height in m/s.
        solar_radiation_wm2: Solar radiation in W/m² (if available).
        is_night: Whether it is night time (no solar heating).

    Returns:
        StabilityClass: One of A–F.
    """
    if wind_speed_ms < 2.0:
        if is_night:
            return StabilityClass.F
        elif solar_radiation_wm2 is None or solar_radiation_wm2 < 200:
            return StabilityClass.E
        else:
            return StabilityClass.A
    elif wind_speed_ms < 3.0:
        if is_night:
            return StabilityClass.E
        elif solar_radiation_wm2 is None or solar_radiation_wm2 < 200:
            return StabilityClass.D
        elif solar_radiation_wm2 < 400:
            return StabilityClass.B
        else:
            return StabilityClass.A
    elif wind_speed_ms < 5.0:
        if is_night:
            return StabilityClass.D
        elif solar_radiation_wm2 is None or solar_radiation_wm2 < 200:
            return StabilityClass.D
        elif solar_radiation_wm2 < 400:
            return StabilityClass.C
        else:
            return StabilityClass.B
    elif wind_speed_ms < 6.0:
        if is_night:
            return StabilityClass.D
        else:
            return StabilityClass.C if solar_radiation_wm2 and solar_radiation_wm2 >= 400 else StabilityClass.D
    else:
        return StabilityClass.D


def get_roughness_length(landuse: str) -> float:
    """
    Surface roughness length (z0) in meters for atmospheric boundary layer modeling.

    Args:
        landuse: Land use category (urban, suburban, park, water, forest, etc).

    Returns:
        Roughness length in meters.
    """
    z0_map = {
        "urban": 2.0,
        "urban_dense": 2.5,
        "suburban": 0.8,
        "park": 0.5,
        "grassland": 0.1,
        "water": 0.001,
        "forest": 1.0,
        "agricultural": 0.2,
        "industrial": 1.5,
    }
    return z0_map.get(landuse.lower(), 0.5)


def get_stability_dispersion_params(stability: StabilityClass) -> tuple[float, float]:
    """
    Pasquill-Gifford dispersion parameters (sigma_y_coeff, sigma_z_coeff) by stability class.

    These parameterize horizontal and vertical plume spread as:
    - sigma_y = sigma_y_coeff * distance
    - sigma_z = sigma_z_coeff * distance

    Args:
        stability: Pasquill stability class.

    Returns:
        (sigma_y_coeff, sigma_z_coeff) in units of 1/distance.
    """
    params = {
        StabilityClass.A: (0.27, 0.20),
        StabilityClass.B: (0.24, 0.12),
        StabilityClass.C: (0.22, 0.08),
        StabilityClass.D: (0.20, 0.06),
        StabilityClass.E: (0.14, 0.03),
        StabilityClass.F: (0.10, 0.016),
    }
    return params.get(stability, (0.20, 0.06))


# Bio-physical constants for human inhalation.
class RespiratoryCostant:
    """Respiratory minute volume (RMV) in m³/hr by transport mode."""

    WALKING = 1.2  # m^3/hr @ ~1.4 m/s walking speed
    CYCLING = 3.5  # m^3/hr @ ~6 m/s cycling speed (elevated due to exertion)
    TWO_WHEELER = 0.6  # m^3/hr currently aligned to legacy driving baseline
    DRIVING_LEGACY_REFERENCE = 0.6  # kept only for historical reference


def get_respiratory_minute_volume(mode: str) -> float:
    """
    Get respiratory minute volume (RMV) in m³/hr for a given travel mode.

    Args:
        mode: Preferred modes are 'walking', 'cycling', 'two_wheeler'.
            Legacy aliases 'driving', 'car', and 'two-wheeler' are supported.

    Returns:
        RMV in m³/hr.

    Raises:
        ValueError: If mode is not recognized.
    """
    mode_lower = mode.lower()
    mode_aliases = {
        "two-wheeler": "two_wheeler",
        "driving": "two_wheeler",
        "car": "two_wheeler",
    }
    mode_normalized = mode_aliases.get(mode_lower, mode_lower)
    rmv_map = {
        "walking": RespiratoryCostant.WALKING,
        "cycling": RespiratoryCostant.CYCLING,
        "two_wheeler": RespiratoryCostant.TWO_WHEELER,
    }
    if mode_normalized not in rmv_map:
        raise ValueError(f"Unknown transport mode: {mode}. Expected one of {list(rmv_map.keys())}")
    return rmv_map[mode_normalized]


# Urban Canyon Parameters
class UrbanCanyon:
    """Street canyon and building interaction constants."""

    HIGH_DENSITY_THRESHOLD = 0.7  # Building density above which canyon tunneling activates
    CANYON_DEFLECTION_STRENGTH = 0.85  # Wind direction alignment strength in dense canyons
    STAGNATION_AMPLIFICATION = 0.15  # Concentration multiplier per unit stagnation


# City-specific instance path mapping (extensible for new cities).
CITY_INSTANCES = {
    "bangalore": {
        "data_dir": BASE_DIR / "data" / "processed",
            "graph_file": BASE_DIR / "data" / "processed" / "graph" / "topology_graph.pt",
            "node_map": BASE_DIR / "data" / "processed" / "graph" / "topology_nodeid_to_index_map.parquet",
        "master_tensor": BASE_DIR / "data" / "processed" / "model_input_node_hourly_features.parquet",
    },
}


def get_city_instance_paths(city: str) -> dict[str, Path]:
    """
    Retrieve instance-specific paths for a given city.

    Args:
        city: City name (e.g., 'bangalore').

    Returns:
        Dictionary with keys: data_dir, graph_file, node_map, master_tensor.

    Raises:
        ValueError: If city is not in CITY_INSTANCES.
    """
    if city.lower() not in CITY_INSTANCES:
        raise ValueError(f"City '{city}' not configured. Available: {list(CITY_INSTANCES.keys())}")
    return CITY_INSTANCES[city.lower()]
