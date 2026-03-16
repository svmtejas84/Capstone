import { useEffect, useMemo, useState } from "react";
import { RouteRequest, RouteResponse, postRoute } from "../api/client";
import { usePlumeStream } from "../hooks/usePlumeStream";

type Props = {
	route: RouteResponse | null;
	request: RouteRequest | null;
	onRouteUpdate: (route: RouteResponse) => void;
};

function pointOnRoute(points: [number, number][], t: number): [number, number] {
	if (points.length === 0) return [0, 0];
	if (points.length === 1) return points[0];

	const segCount = points.length - 1;
	const scaled = Math.max(0, Math.min(0.9999, t)) * segCount;
	const segIndex = Math.floor(scaled);
	const localT = scaled - segIndex;
	const [aLat, aLon] = points[segIndex];
	const [bLat, bLon] = points[segIndex + 1];
	return [aLat + (bLat - aLat) * localT, aLon + (bLon - aLon) * localT];
}

export function AgentSim({ route, request, onRouteUpdate }: Props) {
	const plume = usePlumeStream(5000);
	const [progress, setProgress] = useState(0);
	const [alert, setAlert] = useState<string>("");
	const [rerouting, setRerouting] = useState(false);

	const currentPoint = useMemo(() => {
		if (!route) return null;
		return pointOnRoute(route.route, progress);
	}, [route, progress]);

	useEffect(() => {
		setProgress(0);
		setAlert("");
		setRerouting(false);
	}, [route?.stake_hash]);

	useEffect(() => {
		if (!route) return;
		const id = window.setInterval(() => {
			setProgress((p) => (p >= 1 ? 0 : p + 0.03));
		}, 600);
		return () => window.clearInterval(id);
	}, [route]);

	useEffect(() => {
		if (!request || !currentPoint || !plume?.wake?.geometry?.coordinates?.[0] || rerouting) return;

		const ring = plume.wake.geometry.coordinates[0];
		if (ring.length === 0) return;

		let minLat = Number.POSITIVE_INFINITY;
		let maxLat = Number.NEGATIVE_INFINITY;
		let minLon = Number.POSITIVE_INFINITY;
		let maxLon = Number.NEGATIVE_INFINITY;
		for (const [lon, lat] of ring) {
			if (lat < minLat) minLat = lat;
			if (lat > maxLat) maxLat = lat;
			if (lon < minLon) minLon = lon;
			if (lon > maxLon) maxLon = lon;
		}

		const [lat, lon] = currentPoint;
		const insideWake = lat >= minLat && lat <= maxLat && lon >= minLon && lon <= maxLon;
		if (!insideWake) return;

		setAlert("Pollution wake intersected route, recalculating...");
		setRerouting(true);
		postRoute(request)
			.then((next) => {
				onRouteUpdate(next);
				setAlert("Route adjusted to avoid wake.");
			})
			.catch(() => {
				setAlert("Reroute request failed; retaining current route.");
			})
			.finally(() => {
				setRerouting(false);
			});
	}, [currentPoint, plume, request, rerouting, onRouteUpdate]);

	return (
		<section className="card">
			<h2>Dynamic Reroute</h2>
			<p>Progress: {(progress * 100).toFixed(0)}%</p>
			<p>Agent position: {currentPoint ? `${currentPoint[0].toFixed(5)}, ${currentPoint[1].toFixed(5)}` : "no route yet"}</p>
			<p>{alert || "Monitoring wake intersection..."}</p>
		</section>
	);
}

