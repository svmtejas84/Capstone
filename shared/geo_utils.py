from math import asin, cos, radians, sin, sqrt


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
	r = 6_371_000.0
	d_lat = radians(lat2 - lat1)
	d_lon = radians(lon2 - lon1)
	a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
	return 2 * r * asin(sqrt(a))


def lerp(a: float, b: float, t: float) -> float:
	return a + (b - a) * t

