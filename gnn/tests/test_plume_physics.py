from gnn.plume_physics import (
	dispersion_sigmas,
	effective_wind_speed,
	gaussian_plume,
	urban_canyon_correction,
)


def test_gaussian_plume_positive_for_valid_inputs() -> None:
	val = gaussian_plume(
		q=20.0,
		x_downwind_m=120.0,
		y_crosswind_m=8.0,
		wind_speed=1.2,
		sigma_y=15.0,
		sigma_z=6.0,
	)
	assert val > 0.0


def test_urban_canyon_correction_increases_concentration() -> None:
	base = 10.0
	corrected = urban_canyon_correction(base, building_density=0.8, wind_speed=0.9)
	assert corrected > base


def test_dispersion_sigmas_and_effective_wind() -> None:
	sy, sz = dispersion_sigmas(300.0)
	assert sy > 0.0 and sz > 0.0
	assert effective_wind_speed(2.0, 0.8) < 2.0

