import "./styles/index.css";
import { useState } from "react";
import { RouteRequest, RouteResponse } from "./api/client";
import { AgentSim } from "./components/AgentSim";
import { AuditViewer } from "./components/AuditViewer";
import { EquilibriumViz } from "./components/EquilibriumViz";
import { PlumeMap } from "./components/PlumeMap";
import { RoutePanel } from "./components/RoutePanel";

export default function App() {
	const [stakeHash, setStakeHash] = useState("");
	const [latestRoute, setLatestRoute] = useState<RouteResponse | null>(null);
	const [lastRequest, setLastRequest] = useState<RouteRequest | null>(null);

	const handleRouteUpdate = (route: RouteResponse) => {
		setLatestRoute(route);
		setStakeHash(route.stake_hash);
	};

	return (
		<main className="app-shell">
			<h1>Toxicity Navigation Demo</h1>
			<RoutePanel onRouteUpdate={handleRouteUpdate} onRequestUpdate={setLastRequest} />
			<PlumeMap route={latestRoute?.route ?? null} />
			<AgentSim route={latestRoute} request={lastRequest} onRouteUpdate={handleRouteUpdate} />
			<EquilibriumViz />
			<AuditViewer stakeHash={stakeHash} />
		</main>
	);
}

