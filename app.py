from flask import Flask, render_template, abort
from dotenv import load_dotenv
from search import TMDBClient
import os
import requests
import json

app = Flask(__name__)
load_dotenv()

search_client = None
genre_map = {}
movies = []


# Run once at the start to fetch data from TMDB API
def init_app():
    global search_client, genre_map
    search_client = TMDBClient()
    genre_map = search_client.fetch_genres()


@app.route("/")
def search():
    global movies
    movies = search_client.discover_movies()
    return render_template("search.html", movies=movies)


@app.route("/my_movies.html")
def my_movies():
    global movies
    movies = search_client.search_movies(title="Batman")
    return render_template("my_movies.html", movies=movies)


@app.route("/watched.html")
def watched():
    return render_template("watched.html")


@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    # Look up the movie in your database or list
    global movies
    movie = next((m for m in movies if m["id"] == movie_id), None)
    if movie is None:
        abort(404)
    movie["genre_names"] = [genre_map.get(id, "Unknown") for id in movie.get("genre_ids", [])]
    return render_template("movie_detail.html", movie=movie)


if __name__ == "__main__":
    init_app()
    app.run(debug=True)