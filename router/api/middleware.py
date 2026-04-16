from time import perf_counter

from fastapi import FastAPI, Request


def install_middleware(app: FastAPI) -> None:
	@app.middleware("http")
	async def latency_header(request: Request, call_next):
		t0 = perf_counter()
		response = await call_next(request)
		response.headers["X-Latency-ms"] = f"{(perf_counter() - t0) * 1000.0:.2f}"
		return response

