const API_BASE = "http://localhost:8000";

export type Mode = "jogger" | "cyclist" | "car";

export type RouteRequest = {
	origin: [number, number];
	destination: [number, number];
	mode: Mode;
};

export type RouteResponse = {
	route: [number, number][];
	total_cost_w: number;
	stake_hash: string;
	stable_corridor_id: string;
};

type WakeFeature = {
	type: "Feature";
	geometry: {
		type: "Polygon";
		coordinates: number[][][];
	};
	properties: {
		label: string;
		horizon_minutes: number;
	};
};

export type PlumeResponse = {
	grid: number[][];
	wind_u: number[][];
	wind_v: number[][];
	timestamp: string;
	wake?: WakeFeature;
};

async function parseJson<T>(res: Response): Promise<T> {
	if (!res.ok) {
		throw new Error(`HTTP ${res.status}`);
	}
	return (await res.json()) as T;
}

export async function getHealth(): Promise<{ status: string }> {
	const res = await fetch(`${API_BASE}/health`);
	return parseJson<{ status: string }>(res);
}

export async function getPlume(): Promise<PlumeResponse> {
	const res = await fetch(`${API_BASE}/plume`);
	return parseJson<PlumeResponse>(res);
}

export async function postRoute(body: RouteRequest): Promise<RouteResponse> {
	const res = await fetch(`${API_BASE}/route`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(body),
	});
	return parseJson<RouteResponse>(res);
}

export async function getAudit(stakeHash: string): Promise<{ valid: boolean; timestamp?: string }> {
	const res = await fetch(`${API_BASE}/audit/${stakeHash}`);
	return parseJson<{ valid: boolean; timestamp?: string }>(res);
}

