import { RouteResponse } from "../api/client";
import { usePlumeStream } from "../hooks/usePlumeStream";

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

	const grid = data?.grid ?? [];
	const rows = grid.length;
	const cols = rows > 0 ? grid[0].length : 0;

	let min = Number.POSITIVE_INFINITY;
	let max = Number.NEGATIVE_INFINITY;
	for (const row of grid) {
		for (const cell of row) {
			if (cell < min) min = cell;
			if (cell > max) max = cell;
		}
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
			<p>Grid cells: {rows > 0 ? `${rows} x ${cols}` : "n/a"}</p>
			<div className="map-shell">
				<svg viewBox={`0 0 ${width} ${height}`} className="map-svg" role="img" aria-label="Plume map">
					{rows > 0 &&
						grid.map((row, r) =>
							row.map((cell, c) => {
								const x = (c / cols) * width;
								const y = (r / rows) * height;
								return (
									<rect
										key={`${r}-${c}`}
										x={x}
										y={y}
										width={width / cols + 0.5}
										height={height / rows + 0.5}
										fill={toHeatColor(cell, min, max)}
										opacity={0.78}
									/>
								);
							})
						)}

					{wakePoints.length > 0 && <polygon points={wakePoints} className="wake-shape" />}

					{routePoints.length > 1 && <polyline points={routePoints.join(" ")} className="route-line" />}
				</svg>
			</div>
		</section>
	);
}

