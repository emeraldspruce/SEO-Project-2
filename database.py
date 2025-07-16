import sqlite3

def connect_to_database():
    conn = sqlite3.connect('movie_ranker.db')
    return conn

def init_db():
    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE
        );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            imdb_id TEXT NOT NULL,
            rating REAL,
            title TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
                ON DELETE CASCADE,
            UNIQUE(user_id, imdb_id)
        );
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
