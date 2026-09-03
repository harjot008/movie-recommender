from typing import Any
import requests


def search_movie(tmdb_api_key: str, movie_title: str, release_year: int, ):
    """
        Return the poster image link for a movie.

        Args:
            

        Returns:
            dict[str, Any]
    """

    url: str = "https://api.themoviedb.org/3/search/movie"

    headers: dict[str, str] = {
        "Authorization": f'Bearer {tmdb_api_key}',
        "accept": "application/json"
    }

    params: dict[str, str | int] = {
        "query": movie_title,
        "year": release_year,
        "language": "en-US"
    }

    requests.get(url=url, params=params, headers=headers)

    