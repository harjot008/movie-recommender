from pydantic import BaseModel, Field, field_validator, ValidationError
from datetime import date
from typing import Literal, Optional


# userinput
class UserInput(BaseModel):
    query: str = Field(..., min_length=20, description="Desired movie recommendations personalized to user")


# Each movie model
class Movie(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    genre: Literal[
    "action",
    "comedy",
    "drama",
    "sci-fi",
    "thriller",
    "horror",
    "romance",
    ]
    release_year: int = Field(..., ge=1900)
    @field_validator("release_year")
    @classmethod
    def validateCurrentYear(cls, year: int) -> int:
        if year > date.today().year:
            raise ValueError("The year is greater than current year")
        return year
        
    rating: float = Field(..., ge=0.0, le=10.0)
    synopsis: str = Field(..., min_length=10, max_length=500)
    director: Optional[str] = None
    lead_actor: Optional[str] = None
    recommended_for: Optional[
        Literal["family", "adults", "teens"]
    ] = None


class MovieRecommendations(BaseModel):
    movies: list[Movie] = Field(max_length=10)