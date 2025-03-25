import time

import requests
from logger import logger
from services.config_services import Config


class TMDBService:
    def __init__(self, config: Config):
        self.config = config

    def generate_recommendations(self, movie_id):
        try:
            url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations"
            params = {"api_key": self.config.tmdb_api_key}
            response = requests.get(url, params=params)
            data = response.json()
            ret_list = []

            for movie in data["results"]:
                ret_list.append(movie)

            logger.info(f"Sleeping for {self.config.tmdb_rate_limit} seconds to prevent rate limiting")
            time.sleep(self.config.tmdb_sleep_interval)

            return ret_list

        except Exception as e:
            logger.error(f"Error with TMDB on movie '{movie_id}': {str(e)}")
            return []

    def perform_movie_search(self, query):
        try:
            parsed_results = None
            logger.info(f"Search query: {query}")

            url = f"https://api.themoviedb.org/3/search/movie?api_key={self.config.tmdb_api_key}&query={query}"
            response = requests.get(url)
            response.raise_for_status()

            results = response.json()
            parsed_results = self.parse_movie_data(results.get("results", []))

        except Exception as e:
            logger.error(f"TMDB Search Error: {str(e)}")

        finally:
            return parsed_results

    def parse_movie_data(self, movies):
        parsed_movies = []

        for movie in movies:
            genre_list = self.map_genre_ids_to_names(movie.get("genre_ids"))
            genres = ", ".join(genre_list)
            rounded_popularity = round(movie.get("popularity", 0), 2)
            rounded_vote_average = round(movie.get("vote_average", 0), 2)

            base_link = "https://image.tmdb.org/t/p/w300"
            poster_path = movie.get("poster_path")
            image_link = f"{base_link}{poster_path}" if poster_path else "https://placehold.co/300x200"

            movie_data = {
                "title": movie.get("title"),
                "genres": genres,
                "original_language": movie.get("original_language"),
                "popularity": rounded_popularity,
                "vote_average": rounded_vote_average,
                "vote_count": movie.get("vote_count"),
                "first_air_date": movie.get("release_date"),
                "year": movie.get("release_date")[:4] if movie.get("release_date") else None,
                "tmdb_id": movie.get("id"),
                "image": image_link,
                "overview": movie.get("overview"),
                "status": "",
            }
            parsed_movies.append(movie_data)

        return parsed_movies

    def map_genre_ids_to_names(self, genre_ids):
        genre_mapping = {
            28: "Action",
            12: "Adventure",
            16: "Animation",
            35: "Comedy",
            80: "Crime",
            99: "Documentary",
            18: "Drama",
            10751: "Family",
            14: "Fantasy",
            36: "History",
            27: "Horror",
            10402: "Music",
            9648: "Mystery",
            10749: "Romance",
            878: "Science Fiction",
            10770: "TV Movie",
            53: "Thriller",
            10752: "War",
            37: "Western",
        }
        return [genre_mapping.get(genre_id, "Unknown") for genre_id in genre_ids]
