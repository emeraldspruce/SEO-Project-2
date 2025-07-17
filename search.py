import requests
import json
from urllib.parse import quote
from dotenv import load_dotenv
import os


class TMDBClient:
    def __init__(self, api_key=None, language="en-US", include_adult=False):
        # Get API key
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("TMDB_API_KEY not found.")
        
        self.language = language
        self.include_adult = str(include_adult).lower()
        self.base_url = "https://api.themoviedb.org/3"
        # Remove Bearer token, use simple headers
        self.headers = {
            "accept": "application/json"
        }


    def search_movies(self, title, year=None, page=1, get_all_pages=False, max_results=1000):
        '''Used TMDB's search endpoint to find movies by title.'''
        query = quote(title)
        results = []

        # Add api_key to URL
        url = f"{self.base_url}/search/movie?api_key={self.api_key}&query={query}&include_adult={self.include_adult}&language={self.language}&page={page}"
        if year:
            url += f"&year={year}"

        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.json().get("status_message", "No status message available."))
            return []

        data = response.json()
        total_pages = data.get("total_pages", 0)
        total_results = data.get("total_results", 0)
        results.extend(data.get("results", []))

        # For debugging purposes we can get a large number of results
        if get_all_pages:
            page += 1
            while page <= total_pages and len(results) < max_results:
                url = f"{self.base_url}/search/movie?api_key={self.api_key}&query={query}&include_adult={self.include_adult}&language={self.language}&page={page}"
                if year:
                    url += f"&year={year}"

                response = requests.get(url, headers=self.headers)
                if response.status_code != 200:
                    print(f"Error on page {page}: {response.status_code}")
                    break

                data = response.json()
                results.extend(data.get("results", []))
                page += 1

        print(f"Found {total_results} total results across {total_pages} pages. Fetched {len(results)} results.")
        return results


    def discover_movies(self, sort_by="popularity.desc", year=None, page=1):
        '''Used TMDB's discover endpoint to get a list of current popular movies.'''
        url = f"{self.base_url}/discover/movie?api_key={self.api_key}&sort_by={sort_by}&include_adult={self.include_adult}&language={self.language}&page={page}"
        if year is not None:
            url += f"&primary_release_year={year}"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.json().get("status_message", "No status message available."))
            return []

        data = response.json()
        return data.get("results", [])


    def fetch_genres(self):
        '''Fetches the list of movie genres from TMDB and stores them in a dictionary.'''
        url = f"{self.base_url}/genre/movie/list?api_key={self.api_key}&language={self.language}"
        response = requests.get(url, headers=self.headers)
        self.genre_map = {}

        if response.status_code == 200:
            data = response.json()
            self.genre_map = {genre['id']: genre['name'] for genre in data.get('genres', [])}
        else:
            print(f"Error fetching genres: {response.status_code}")


    def genre_ids_to_names(self, genre_ids):
        '''Convert a list of genre IDs to their names using the genre_map.'''
        if not hasattr(self, 'genre_map'):
            self.fetch_genres()
        return [self.genre_map.get(genre_id, "Unknown") for genre_id in genre_ids]


    def save_to_file(self, results, filename="movies.json"):
        '''The intent of this function is to serve as a debug tool to save on API calls.'''
        with open(filename, "w") as file:
            json.dump(results, file, indent=2)
        print(f"Saved {len(results)} results to {filename}")