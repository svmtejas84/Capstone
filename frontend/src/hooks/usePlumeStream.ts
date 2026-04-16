import { useEffect, useState } from "react";
import { getPlume, PlumeResponse } from "../api/client";

export function usePlumeStream(intervalMs = 15000) {
	const [data, setData] = useState<PlumeResponse | null>(null);

	useEffect(() => {
		let alive = true;

		const tick = async () => {
			try {
				const plume = await getPlume();
				if (alive) setData(plume);
			} catch {
				if (alive) setData(null);
			}
		};

		tick();
		const timer = setInterval(tick, intervalMs);
		return () => {
			alive = false;
			clearInterval(timer);
		};
	}, [intervalMs]);

	return data;
}

