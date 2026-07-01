"""
title: IMDB Most Popular Movies
author: aviad
version: 1.1.0
license: MIT
description: Fetches the most popular movies from a local FastAPI bridge server and returns them as clean, readable text for the LLM.
requirements: requests
"""

import requests
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        server_url: str = Field(
            default="http://host.docker.internal:5005/popular",
            description=(
                "URL of the local FastAPI server endpoint that returns popular "
                "movies. Use host.docker.internal so the Open-WebUI container can "
                "reach the server running on the Windows host."
            ),
        )
        max_movies: int = Field(
            default=5,
            description="Maximum number of movies to include in the answer.",
        )
        timeout: int = Field(
            default=15,
            description="HTTP request timeout in seconds.",
        )

    def __init__(self):
        self.valves = self.Valves()

    def get_most_popular_movies(self) -> str:
        """
        Get the current list of the most popular movies from IMDB.
        Use this whenever the user asks about popular, trending, or top movies.

        :return: A human-readable, numbered list of the most popular movies.
        """
        url = self.valves.server_url

        try:
            response = requests.get(url, timeout=self.valves.timeout)
        except Exception as e:
            return (
                f"Failed to connect to the local movie server at {url}. "
                f"Make sure tools_server.py is running on the host and that the "
                f"Open-WebUI container can reach it. Details: {e}"
            )

        if response.status_code != 200:
            return f"Error: the movie server returned status code {response.status_code}."

        try:
            data = response.json()
        except Exception as e:
            return f"Error: could not parse the movie server response as JSON. Details: {e}"

        movies = data if isinstance(data, list) else data.get("results", data.get("data", []))
        if not isinstance(movies, list) or not movies:
            return "No movies were returned by the server."

        lines = ["Here are the most popular movies right now:\n"]
        for i, movie in enumerate(movies[: self.valves.max_movies], start=1):
            if not isinstance(movie, dict):
                lines.append(f"{i}. {movie}")
                continue

            title = (
                movie.get("primaryTitle")
                or movie.get("originalTitle")
                or movie.get("title")
                or "Unknown title"
            )
            year = movie.get("startYear") or movie.get("year") or ""
            rating = movie.get("averageRating") or movie.get("rating") or ""
            genres = movie.get("genres") or []
            if isinstance(genres, list):
                genres = ", ".join(str(g) for g in genres)

            details = []
            if year:
                details.append(f"Year: {year}")
            if rating:
                details.append(f"IMDb rating: {rating}")
            if genres:
                details.append(f"Genres: {genres}")

            suffix = f" ({'; '.join(details)})" if details else ""
            lines.append(f"{i}. {title}{suffix}")

        return "\n".join(lines)
