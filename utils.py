from typing import Any
import requests


def search_movie(tmdb_api_key: str | None, movie_title: str, release_year: int, ):
    """Search TMDB for a movie matching the supplied title and release year."""

    if not tmdb_api_key:
        raise ValueError("TMDB API key was not found.")

    url = "https://api.themoviedb.org/3/search/movie"

    headers = {
        "accept": "application/json",
    }

    params: dict[str, str | int | bool] = {
        "api_key": tmdb_api_key,
        "query": movie_title,
        "primary_release_year": release_year,
        "language": "en-US",
        "include_adult": False,
    }

    response = requests.get(
        url=url,
        params=params,
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()

    data: dict[str, Any] = response.json()
    results = data.get("results")

    if not isinstance(results, list) or not results:
        return None

    return results[0]
