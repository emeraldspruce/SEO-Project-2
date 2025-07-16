import sqlite3

class MovieRankerDB:
    def __init__(self, db_path='movie_ranker.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        # Users table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """)

        # Movies table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            adult BOOLEAN NOT NULL,
            backdrop_path TEXT,
            poster_path TEXT,
            original_language TEXT,
            title TEXT NOT NULL,
            overview TEXT,
            release_date TEXT,
            vote_average REAL,
            vote_count INTEGER,
            popularity REAL
        )
        """)

        # User_Movies table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_movies (
            user_id INTEGER,
            movie_id INTEGER,
            rating INTEGER NOT NULL,
            PRIMARY KEY (user_id, movie_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id)
        )
        """)

        # Genre_Map table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS genre_map (
            movie_id INTEGER,
            genre_id INTEGER,
            PRIMARY KEY (movie_id, genre_id),
            FOREIGN KEY (movie_id) REFERENCES movies(id)
        )
        """)

        self.conn.commit()

    def add_user(self, name):
        self.cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_movie(self, movie_data):
        self.add_genres(movie_data['id'], movie_data.get('genre_ids', []))
        self.cursor.execute("""
        INSERT OR IGNORE INTO movies (id, adult, backdrop_path, poster_path, original_language, title, overview, release_date, vote_average, vote_count, popularity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            movie_data['id'], movie_data['adult'], movie_data.get('backdrop_path'),
            movie_data.get('poster_path'), movie_data['original_language'], movie_data['title'],
            movie_data.get('overview'), movie_data.get('release_date'), movie_data.get('vote_average', 0),
            movie_data.get('vote_count', 0), movie_data.get('popularity', 0)
        ))
        self.conn.commit()

    def add_user_movie_by_id(self, user_id, movie_id, rating):
        self.cursor.execute("""
        INSERT OR REPLACE INTO user_movies (user_id, movie_id, rating)
        VALUES (?, ?, ?)
        """, (user_id, movie_id, rating))
        self.conn.commit()

    def add_user_movie_by_name(self, user_name, movie_id, rating):
        self.cursor.execute("""
        INSERT OR REPLACE INTO user_movies (user_id, movie_id, rating)
        VALUES ((SELECT id FROM users WHERE name = ?), ?, ?)
        """, (user_name, movie_id, rating))
        self.conn.commit()

    def add_genre(self, movie_id, genre_id):
        self.cursor.execute("""
        INSERT OR IGNORE INTO genre_map (movie_id, genre_id)
        VALUES (?, ?)
        """, (movie_id, genre_id))
        self.conn.commit()

    def add_genres(self, movie_id, genre_ids):
        for genre_id in genre_ids:
            self.add_genre(movie_id, genre_id)

    def get_user_movies(self, user_name, sort_by="rating", ascending=False):
        sort_fields = {
            "rating": "um.rating",
            "popularity": "m.popularity",
            "title": "m.title",
            "vote_average": "m.vote_average",
            "vote_count": "m.vote_count",
            "release_date": "m.release_date"
        }

        sort_column = sort_fields.get(sort_by)
        if not sort_column:
            raise ValueError(f"Invalid sort field '{sort_by}'. Must be one of: {', '.join(valid_sort_fields)}")

        order = "ASC" if ascending else "DESC"
        self.cursor.execute(f"""
            SELECT m.*, um.rating
            FROM users u
            JOIN user_movies um ON u.id = um.user_id
            JOIN movies m ON um.movie_id = m.id
            WHERE u.name = ?
            ORDER BY {sort_column} {order}
        """, (user_name,))
        return self.cursor.fetchall()

    def get_movie_data(self, movie_id):
        self.cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
        return self.cursor.fetchone()

    def rm_user_by_name(self, user_name):
        self.cursor.execute("DELETE FROM users WHERE name = ?", (user_name,))
        self.conn.commit()

    def rm_user_by_id(self, user_id):
        self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.conn.commit()

    def rm_user_movie_by_name(self, user_name, movie_id):
        self.cursor.execute("""
        DELETE FROM user_movies
        WHERE user_id = (SELECT id FROM users WHERE name = ?) AND movie_id = ?
        """, (user_name, movie_id))
        self.conn.commit()

    def rm_user_movie_by_id(self, user_id, movie_id):
        self.cursor.execute("""
        DELETE FROM user_movies
        WHERE user_id = ? AND movie_id = ?
        """, (user_id, movie_id))
        self.conn.commit()

    def rm_movie(self, movie_id):
        self.cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

    # Debug methods
    def print_all_users(self):
        '''Prints all users to the console.'''
        self.cursor.execute("SELECT * FROM users")
        users = self.cursor.fetchall()
        for user in users:
            print(f"User ID: {user['id']}, Name: {user['name']}")

    def print_all_movies(self):
        '''Prints all movies to the console.'''
        self.cursor.execute("SELECT * FROM movies")
        movies = self.cursor.fetchall()
        for movie in movies:
            print(f"Movie ID: {movie['id']}, Title: {movie['title']}, Rating: {movie['vote_average']}")

    def print_all_user_movies(self, user_name):
        '''Prints all movies for a specific user to the console.'''
        self.cursor.execute("""
            SELECT m.*, um.rating
            FROM users u
            JOIN user_movies um ON u.id = um.user_id
            JOIN movies m ON um.movie_id = m.id
            WHERE u.name = ?
        """, (user_name,))
        user_movies = self.cursor.fetchall()
        for movie in user_movies:
            print(f"Movie ID: {movie['id']}, Title: {movie['title']}, Rating: {movie['rating']}")

    def clear_database(self):
        '''Clears all data from the database.'''
        self.cursor.execute("DELETE FROM user_movies")
        self.cursor.execute("DELETE FROM genre_map")
        self.cursor.execute("DELETE FROM movies")
        self.cursor.execute("DELETE FROM users")
        self.conn.commit()
