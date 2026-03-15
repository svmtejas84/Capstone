from pydantic import BaseModel


class Settings(BaseModel):
    redis_url: str = "redis://localhost:6379/0"
    default_city: str = "Bangalore"
    physics_grid_resolution_m: int = 100
    nowcast_interval_seconds: int = 300


settings = Settings()
