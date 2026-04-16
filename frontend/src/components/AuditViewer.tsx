import { useEffect, useState } from "react";
import { getAudit } from "../api/client";

type Props = {
	stakeHash: string;
};

export function AuditViewer({ stakeHash }: Props) {
	const [result, setResult] = useState<any>(null);

	useEffect(() => {
		if (!stakeHash) return;
		getAudit(stakeHash).then(setResult).catch(() => setResult({ valid: false }));
	}, [stakeHash]);

	return (
		<section className="card">
			<h2>Stake Audit</h2>
			<p>Hash: {stakeHash || "none"}</p>
			<p>Valid: {result?.valid ? "true" : "false"}</p>
		</section>
	);
}

