import { useState } from "react";
import { postRoute, RouteRequest, RouteResponse } from "../api/client";

export function useRouteResult() {
	const [data, setData] = useState<RouteResponse | null>(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const requestRoute = async (payload: RouteRequest): Promise<RouteResponse> => {
		setLoading(true);
		setError(null);
		try {
			const result = await postRoute(payload);
			setData(result);
			return result;
		} catch (e) {
			setError("Failed to fetch route");
			throw e;
		} finally {
			setLoading(false);
		}
	};

	return { data, loading, error, requestRoute };
}

