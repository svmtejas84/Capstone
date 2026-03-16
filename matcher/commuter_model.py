from pydantic import BaseModel


class Commuter(BaseModel):
	id: str
	mode: str
	id_min: float

