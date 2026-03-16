from pydantic import BaseModel


class Segment(BaseModel):
	id: str
	cedge_mean: float
	capacity: int

