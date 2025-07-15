from flask import Flask, render_template

app = Flask(__name__)

# Sample movie data
movies = [
    {"id": 1, "title": "Inception", "rating": 8.8, "summary": "A mind-bending thriller."},
    {"id": 2, "title": "Interstellar", "rating": 8.6, "summary": "A journey through space and time."},
    {"id": 3, "title": "The Dark Knight", "rating": 9.0, "summary": "A gritty superhero film."},
]

@app.route("/")
def search():
    return render_template("search.html")

@app.route("/my_movies.html")
def my_movies():
    return render_template("my_movies.html", movies=movies)

@app.route("/watched.html")
def watched():
    return render_template("watched.html")

@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    # Look up the movie in your database or list
    movie = next((m for m in movies if m["id"] == movie_id), None)
    if movie is None:
        abort(404)
    return render_template("movie_detail.html", movie=movie)

if __name__ == "__main__":
    app.run(debug=True)