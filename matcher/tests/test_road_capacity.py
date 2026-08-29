from matcher.road_capacity import route_capacity


def test_route_capacity_uses_lanes_road_type_and_congestion() -> None:
	wide_primary = route_capacity(
		[{"highway": "primary", "lanes": "3", "congestion": 0.0}],
		travel_time_s=300.0,
	)
	congested_residential = route_capacity(
		[{"highway": "residential", "lanes": "1", "congestion": 0.5}],
		travel_time_s=300.0,
	)

	assert wide_primary > congested_residential


def test_route_capacity_uses_the_bottleneck_segment() -> None:
	wide_only = route_capacity([{"highway": "primary", "lanes": "3"}], travel_time_s=120.0)
	bottlenecked = route_capacity(
		[{"highway": "primary", "lanes": "3"}, {"highway": "service", "lanes": "1"}],
		travel_time_s=120.0,
	)

	assert bottlenecked < wide_only
