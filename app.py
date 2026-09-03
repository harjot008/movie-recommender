import streamlit as st
import os
from recommend import UserInput, MovieRecommendations
from pydantic import ValidationError
from requests import RequestException
from typing import Any
from dotenv import load_dotenv
from google import genai
from google.genai import types
from utils import search_movie

# Initializing with loading keys of TMDB, and gemini api
load_dotenv("key.env")

gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")  
tmdb_api_key: str | None = os.getenv("TMDB_API_KEY")  

# Streamlit importing keys
if gemini_api_key is None:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]

if tmdb_api_key is None:
    tmdb_api_key = st.secrets["TMDB_API_KEY"]

st.set_page_config(
    page_title="Movie Recommender",
    layout="centered"
)

st.title("Movie Recommender")

if gemini_api_key is None:
    st.error("Gemini API key was not found.")
    st.stop()

if tmdb_api_key is None:
    st.error("TMDB API key was not found.")
    st.stop()

client = genai.Client(api_key=gemini_api_key)

with st.form("movie_recommendation_form"):
    movie_input = st.text_input(
        "Describe the kind of movie you want",
        placeholder="For example: Recommend an emotional sci-fi movie about space.",
    )
    submitted = st.form_submit_button("Recommend movies")

if submitted:
    try:
        movie_query = UserInput(query=movie_input.strip())
    except ValidationError:
        st.error("Your query must contain at least 20 characters.")
        st.stop()

    try:
        with st.spinner("Finding recommendations..."):
            response: Any = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=movie_query.query,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are a movie recommendation expert. "
                        "Provide accurate movie recommendations with ratings and details. "
                        "Rank the recommendations from best match to weakest match "
                        "based on the user's query. "
                        "Only include movies that are reasonably relevant."
                    ),
                    response_mime_type="application/json",
                    response_schema=MovieRecommendations,
                ),
            )

        if not response.text:
            st.error("Gemini returned an empty response.")
            st.stop()

        recommendations = MovieRecommendations.model_validate_json(response.text)

    except ValidationError:
        st.error("Gemini returned recommendations in an invalid format.")
        st.stop()
    except Exception as error:
        st.error(f"Could not generate recommendations: {error}")
        st.stop()

    for movie in recommendations.movies:
        try:
            movie_details = search_movie(
                tmdb_api_key,
                movie.title,
                movie.release_year,
            )
        # This error is generated hwen TMDB can not load information for a movie
        except RequestException as error:
            st.warning(f"Could not load TMDB information for {movie.title}: {error}")
            continue
        # ValueError when key is not present
        except ValueError as error:
            st.warning(str(error))
            continue

        if movie_details is None:
            st.warning(
                f"TMDB information was not found for "
                f"{movie.title} ({movie.release_year})."
            )
            continue

        st.subheader(movie_details.get("title", movie.title))

        release_date = movie_details.get("release_date")
        if release_date:
            st.write(f"Release date: {release_date}")

        st.write(f"Recommendation rating: {movie.rating}/10")

        overview = movie_details.get("overview") or movie.synopsis
        st.write(overview)

        poster_path = movie_details.get("poster_path")
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            st.image(
                poster_url,
                caption=movie_details.get("title", movie.title),
            )

        st.divider()