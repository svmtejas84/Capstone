import { RouteResponse } from "../api/client";
import { usePlumeStream } from "../hooks/usePlumeStream";
import { cellToBoundary, latLngToCell, polygonToCells } from "h3-js";

type Props = {
	route: RouteResponse["route"] | null;
};

const BBOX = {
	latMin: 12.834,
	latMax: 13.144,
	lonMin: 77.461,
	lonMax: 77.781,
};

function project(lat: number, lon: number, width: number, height: number): [number, number] {
	const x = ((lon - BBOX.lonMin) / (BBOX.lonMax - BBOX.lonMin)) * width;
	const y = (1 - (lat - BBOX.latMin) / (BBOX.latMax - BBOX.latMin)) * height;
	return [x, y];
}

function toHeatColor(value: number, min: number, max: number): string {
	const ratio = max > min ? (value - min) / (max - min) : 0;
	const r = Math.round(25 + ratio * 220);
	const g = Math.round(170 - ratio * 110);
	const b = Math.round(215 - ratio * 170);
	return `rgb(${r}, ${g}, ${b})`;
}

export function PlumeMap({ route }: Props) {
	const data = usePlumeStream();
	const width = 860;
	const height = 360;
	const res = 9;
	const bboxPoly: [number, number][][] = [[
		[BBOX.latMin, BBOX.lonMin],
		[BBOX.latMin, BBOX.lonMax],
		[BBOX.latMax, BBOX.lonMax],
		[BBOX.latMax, BBOX.lonMin],
		[BBOX.latMin, BBOX.lonMin],
	]];
	const allCells = polygonToCells(bboxPoly, res, true);

	const hexAgg = new Map<string, { sum: number; count: number }>();
	for (const c of allCells) {
		hexAgg.set(c, { sum: 0, count: 0 });
	}
	for (const edge of data?.edges ?? []) {
		const cell = latLngToCell(edge.lat, edge.lon, res);
		const curr = hexAgg.get(cell) ?? { sum: 0, count: 0 };
		curr.sum += edge.toxicity;
		curr.count += 1;
		hexAgg.set(cell, curr);
	}

	let min = Number.POSITIVE_INFINITY;
	let max = Number.NEGATIVE_INFINITY;
	const filledCells: Array<{ cell: string; value: number }> = [];
	for (const [cell, agg] of hexAgg.entries()) {
		if (agg.count <= 0) continue;
		const value = agg.sum / agg.count;
		filledCells.push({ cell, value });
		if (value < min) min = value;
		if (value > max) max = value;
	}
	if (!Number.isFinite(min) || !Number.isFinite(max)) {
		min = 0;
		max = 1;
	}

	const routePoints =
		route?.map(([lat, lon]) => {
			const [x, y] = project(lat, lon, width, height);
			return `${x},${y}`;
		}) ?? [];

	const wakeRing = data?.wake?.geometry?.coordinates?.[0] ?? [];
	const wakePoints = wakeRing
		.map(([lon, lat]) => {
			const [x, y] = project(lat, lon, width, height);
			return `${x},${y}`;
		})
		.join(" ");

	return (
		<section className="card">
			<h2>Live Plume</h2>
			<p>Timestamp: {data?.timestamp ?? "loading"}</p>
			<p>H3 cells (res 9): {filledCells.length}</p>
			<div className="map-shell">
				<svg viewBox={`0 0 ${width} ${height}`} className="map-svg" role="img" aria-label="Plume map">
					{filledCells.map(({ cell, value }) => {
						const boundary = cellToBoundary(cell, true);
						const points = boundary
							.map(([lat, lon]) => {
								const [x, y] = project(lat, lon, width, height);
								return `${x},${y}`;
							})
							.join(" ");
						return (
							<polygon
								key={cell}
								points={points}
								fill={toHeatColor(value, min, max)}
								opacity={0.56}
								stroke="rgba(255,255,255,0.18)"
								strokeWidth={0.6}
							/>
						);
					})}

					{wakePoints.length > 0 && <polygon points={wakePoints} className="wake-shape" />}

					{routePoints.length > 1 && <polyline points={routePoints.join(" ")} className="route-line" />}
				</svg>
			</div>
		</section>
	);
}

