from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router.api.dependencies import init_store
from router.api.middleware import install_middleware
from router.api.routes import router
from shared.config import get_settings


@asynccontextmanager
async def lifespan(_: FastAPI):
	init_store()
	yield


def create_app() -> FastAPI:
	settings = get_settings()
	app = FastAPI(title="toxicity-nav api", version="0.1.0", lifespan=lifespan)

	app.add_middleware(
		CORSMiddleware,
		allow_origins=[settings.frontend_origin],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	install_middleware(app)
	app.include_router(router)

	return app


app = create_app()

