from flask import Flask, render_template, abort, request
from dotenv import load_dotenv
from search import TMDBClient
import database
import os
import requests
import json
import sqlite3


app = Flask(__name__)
load_dotenv()

search_client = None
movies = []


# Run once at the start to fetch data from TMDB API
def init_app():
    global search_client, database

    # Initialize the database
    database = database.MovieRankerDB()

    # Initialize the TMDB client with the API key from environment variables
    api_key = os.getenv("TMDB_API_KEY")
    search_client = TMDBClient(api_key=api_key)


@app.route("/")
def search():
    global movies
    query = request.args.get('query')
    if query:
        movies = search_client.search_movies(title=query)
    else:
        movies = search_client.discover_movies()
    return render_template("search.html", movies=movies, query=query)


@app.route("/my_movies.html")
def my_movies():
    global movies
    movies = search_client.search_movies(title="Batman")
    return render_template("my_movies.html", movies=movies)


@app.route("/watched.html")
def watched():
    global database
    return render_template("watched.html")


@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    # Look up the movie in your database or list
    global movies
    movie = next((m for m in movies if m["id"] == movie_id), None)
    if movie is None:
        abort(404)
    movie["genre_names"] = search_client.genre_ids_to_names(movie.get("genre_ids", []))
    return render_template("movie_detail.html", movie=movie)


if __name__ == "__main__":
    init_app()
    app.run(debug=True)