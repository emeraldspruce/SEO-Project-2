import requests
import json
from urllib.parse import quote
from dotenv import load_dotenv
import os

class TMDBClient:
    def __init__(self, api_key=None, language="en-US", include_adult=False):
        # Get API key
        load_dotenv()
        self.api_key = api_key or os.getenv("TMDB_API_KEY")
        if not self.api_key:
            raise ValueError("TMDB_API_KEY not found.")
        
        self.language = language
        self.include_adult = str(include_adult).lower()
        self.base_url = "https://api.themoviedb.org/3"
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def search_movies(self, title, year=None, page=1, get_all_pages=False, max_results=1000):
        query = quote(title)
        results = []

        url = f"{self.base_url}/search/movie?query={query}&include_adult={self.include_adult}&language={self.language}&page={page}"
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
                url = f"{self.base_url}/search/movie?query={query}&include_adult={self.include_adult}&language={self.language}&page={page}"
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
        url = f"{self.base_url}/discover/movie?sort_by={sort_by}&include_adult={self.include_adult}&language={self.language}&page={page}"
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
        url = f"{self.base_url}/genre/movie/list?language={self.language}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            return {genre['id']: genre['name'] for genre in data.get('genres', [])}
        else:
            print(f"Error fetching genres: {response.status_code}")
            return {}

    def save_to_file(self, results, filename="movies.json"):
        '''The intent of this function is to serve as a debug tool to save on API calls.'''
        with open(filename, "w") as file:
            json.dump(results, file, indent=2)
        print(f"Saved {len(results)} results to {filename}")