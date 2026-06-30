import os
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "").strip()
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "moviesdatabase.p.rapidapi.com").strip()


app = FastAPI(
    title="Netflix Live Movie Tool",
    description="A local Python server that searches movie and TV show information using RapidAPI MoviesDatabase.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", operation_id="health_check")
def health_check():
    return {
        "status": "ok",
        "message": "tools_server.py is running",
        "rapidapi_host": RAPIDAPI_HOST,
        "rapidapi_key_configured": bool(RAPIDAPI_KEY),
        "api_key_length": len(RAPIDAPI_KEY),
        "api_key_last_4_chars": RAPIDAPI_KEY[-4:] if RAPIDAPI_KEY else None,
    }


@app.get("/search_title", operation_id="search_movie_or_tv_title")
def search_title(
    title: str = Query(..., description="Movie or TV show title to search for"),
    title_type: str = Query("movie", description="Type of title, for example: movie or tvSeries"),
):
    if not RAPIDAPI_KEY:
        raise HTTPException(
            status_code=500,
            detail="RAPIDAPI_KEY is missing. Check your .env file.",
        )

    encoded_title = quote(title)

    url = f"https://{RAPIDAPI_HOST}/titles/search/title/{encoded_title}"

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
    }

    params = {
        "titleType": title_type,
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=20,
        )

    except requests.exceptions.RequestException as error:
        raise HTTPException(
            status_code=502,
            detail=f"RapidAPI connection failed: {str(error)}",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "RapidAPI request failed",
                "rapidapi_status_code": response.status_code,
                "rapidapi_response": response.text,
                "url_called": url,
                "params_sent": params,
                "host_sent": RAPIDAPI_HOST,
                "api_key_loaded": bool(RAPIDAPI_KEY),
                "api_key_length": len(RAPIDAPI_KEY),
                "api_key_last_4_chars": RAPIDAPI_KEY[-4:] if RAPIDAPI_KEY else None,
            },
        )

    data = response.json()

    results = data.get("results", [])

    simplified_results = []

    for item in results[:5]:
        title_text = item.get("titleText", {}).get("text")
        title_type_data = item.get("titleType", {}).get("text")
        release_year = item.get("releaseYear", {}).get("year")
        release_date = item.get("releaseDate")

        simplified_results.append(
            {
                "id": item.get("id"),
                "title": title_text,
                "type": title_type_data,
                "release_year": release_year,
                "release_date": release_date,
            }
        )

    return {
        "searched_title": title,
        "title_type_filter": title_type,
        "source": "RapidAPI MoviesDatabase",
        "total_results": len(results),
        "top_results": simplified_results,
    }