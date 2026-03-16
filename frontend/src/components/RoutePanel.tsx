import { useState } from "react";
import { RouteRequest, RouteResponse } from "../api/client";
import { useRouteResult } from "../hooks/useRouteResult";

type Props = {
	onRouteUpdate: (route: RouteResponse) => void;
	onRequestUpdate: (request: RouteRequest) => void;
};

export function RoutePanel({ onRouteUpdate, onRequestUpdate }: Props) {
	const [mode, setMode] = useState<RouteRequest["mode"]>("jogger");
	const { data, loading, requestRoute } = useRouteResult();

	const submit = async () => {
		const payload: RouteRequest = {
			origin: [13.035, 77.596],
			destination: [12.975, 77.607],
			mode,
		};
		const res = await requestRoute(payload);
		onRequestUpdate(payload);
		onRouteUpdate(res);
	};

	return (
		<section className="card">
			<h2>Route Panel</h2>
			<select value={mode} onChange={(e) => setMode(e.target.value as RouteRequest["mode"])}>
				<option value="jogger">Jogger</option>
				<option value="cyclist">Cyclist</option>
				<option value="car">Car</option>
			</select>
			<button onClick={submit} disabled={loading}>{loading ? "Routing..." : "Request Route"}</button>
			{data && <p>Cost W: {data.total_cost_w.toFixed(6)}</p>}
			{data && <p>Corridor: {data.stable_corridor_id}</p>}
		</section>
	);
}

