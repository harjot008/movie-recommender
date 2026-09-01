import streamlit as st
import os
from recommend import UserInput, MovieRecommendations
from pydantic import ValidationError
from typing import Any
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Initializing with loading keys of TMDB, and gemini api
load_dotenv("key.env")

api_key: str | None = os.getenv("GEMINI_API_KEY")  
tmdb_api_key: str | None = os.getenv("TMDB_API_KEY")  

if api_key is None:
    raise ValueError("The key was not found")

client = genai.Client(api_key=api_key)
st.set_page_config(
    page_title="Movie Recommender",
    layout="centered"
)

st.title("Movie Recommender")

movie_input: str | None = st.text_input(
    "What movie do you want?",
    placeholder="What movie you want!"
)

# Validating user query
movie_query: UserInput | None = None

if movie_input:
    try:
        movie_query = UserInput(query=movie_input)

    except ValidationError:
        st.text("Query should be of min length of 20 characters")

# Getting the movie recommendation from gemini llm
if not movie_query is None:
    # Call the gemini by giving the UserInput model
    # And getting the recommendations in form of MovieRecommendation model
    response: Any = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=movie_query.query,
        config=types.GenerateContentConfig(
			system_instruction=(
				"You are a movie recommendation expert. "
				"Provide accurate movie recommendations with ratings and details."
                "Rank the recommendations from best match to weakest match based on the user's query. "
    			"Only include movies that are reasonably relevant."
			),
			response_mime_type="application/json",
			response_schema=MovieRecommendations
        )
    )

	# Validate Gemini response using Pydantic
    recommendations: MovieRecommendations = (
        MovieRecommendations.model_validate_json(response.text)
	)

    # Display movies
    for movie in recommendations.movies:
        st.subheader(movie.title)
        st.write("Year:", movie.release_year)
        st.write("Rating:", movie.rating)
        st.write("Synopsis:", movie.synopsis)