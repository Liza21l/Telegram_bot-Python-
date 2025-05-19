from pydantic import BaseModel


class Film(BaseModel):
    name: str
    description: str
    year: float
    rating: float
    genre: str
    actors: list[str]
    poster: str
