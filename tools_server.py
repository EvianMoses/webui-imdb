from fastapi import FastAPI
import requests
import uvicorn

app = FastAPI()

RAPIDAPI_URL = "https://imdb236.p.rapidapi.com/api/imdb/most-popular-movies"
HEADERS = {
    "x-rapidapi-key": "f1a1aa0a13msh6d1d352d2d8a123p1ecd27jsn626b1584eb83",
    "x-rapidapi-host": "imdb236.p.rapidapi.com",
    "Content-Type": "application/json",
}


def _slim(movie: dict) -> dict:
    """Keep only the fields the tool/LLM actually needs."""
    return {
        "primaryTitle": movie.get("primaryTitle") or movie.get("originalTitle"),
        "startYear": movie.get("startYear"),
        "averageRating": movie.get("averageRating"),
        "genres": movie.get("genres"),
    }


@app.get("/popular")
def get_popular_movies():
    try:
        response = requests.get(RAPIDAPI_URL, headers=HEADERS, timeout=15)
    except Exception as e:
        return {"error": str(e)}

    if response.status_code != 200:
        return {"error": f"API returned status {response.status_code}"}

    data = response.json()
    if isinstance(data, list):
        return [_slim(m) for m in data[:5] if isinstance(m, dict)]
    return data


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5005)
