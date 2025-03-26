import json
import os

import requests
from db.movie_db_handler import MovieDBHandler
from logger import logger
from services.config_services import Config
from services.tmdb_services import TMDBService
from unidecode import unidecode


class RadarrService:
    def __init__(self, config: Config, db: MovieDBHandler):
        self.config = config
        self.db = db
        self.tmdb_service = TMDBService(config)

    def generate_and_store_tmbd_recommendations(self):
        try:
            radarr_movie_items = self.db.get_existing_db_movies()

            for movie_item in radarr_movie_items:
                movie_title = movie_item.get("title")
                movie_tmdb_id = movie_item.get("tmdb_id")
                logger.info(f"Processing movie: {movie_title}")

                has_existing_recommendations = self.db._get_recommended_movies_for_radarr_movie(movie_title)

                if not has_existing_recommendations:
                    recommendations = self.tmdb_service.generate_recommendations(movie_tmdb_id)

                    if recommendations:
                        parsed_recommendations = self.tmdb_service.parse_movie_data(recommendations)
                        self.db.store_recommended_movies_for_radarr_movie(movie_title, parsed_recommendations)
                    else:
                        logger.warning(f"No recommendations found for movie: {movie_title}")
                else:
                    logger.info(f"Movie {movie_title} already has recommendations in the database.")

        except Exception as e:
            logger.error(f"Error generating and storing LastFM recommendations: {str(e)}")
            return "Failed"

        else:
            return "Completed"

    def refresh_radarr_movies(self):
        try:
            updated_radarr_movies = self._get_movies()
            self.db.add_radarr_movies(updated_radarr_movies)

        except Exception as e:
            logger.error(f"Error Refreshing Radarr Movies: {str(e)}")
            return "Failed"

        else:
            return "Completed"

    def _get_movies(self):
        try:
            logger.info("Getting Movies from Radarr")
            endpoint = f"{self.config.radarr_address}/api/v3/movie"
            headers = {"X-Api-Key": self.config.radarr_api_key}
            response = requests.get(endpoint, headers=headers, timeout=self.config.radarr_api_timeout)

            if response.status_code == 200:
                return response.json() or []
            else:
                logger.error(f"Radarr Error Code: {response.status_code}")
                logger.error(f"Radarr Error Message: {response.text}")
                return []

        except requests.RequestException as e:
            logger.error(f"Radarr API Request Failed: {str(e)}")
            raise

    def add_movie_to_radarr(self, movie_title, tmdb_id):
        try:
            movie_folder = movie_title.replace("/", " ")
            radarr_url = f"{self.config.radarr_address}/api/v3/movie"
            headers = {"X-Api-Key": self.config.radarr_api_key}
            payload = {
                "title": movie_title,
                "qualityProfileId": self.config.radarr_quality_profile_id,
                "metadataProfileId": self.config.radarr_metadata_profile_id,
                "titleSlug": movie_title.lower().replace(" ", "-"),
                "rootFolderPath": self.config.radarr_root_folder_path,
                "tmdbId": tmdb_id,
                "monitored": True,
                "addOptions": {
                    "monitor": "movieOnly",
                    "searchForMovie": self.config.radarr_search_for_missing_movies,
                },
            }

            response = requests.post(radarr_url, headers=headers, json=payload)

            if response.status_code == 201:
                logger.info(f"Movie '{movie_title}' added successfully to Radarr.")
                return {"result": "success", "message": "Movie added successfully.", "status": "Added"}

            error_data = json.loads(response.content)
            error_message = error_data[0].get("errorMessage", "Unknown Error")

            if "already exists in the database" in error_message or "already been added" in error_message:
                status = "Already in Radarr"
                logger.info(f"Movie '{movie_title}' is already in Radarr.")
            elif "configured for an existing movie" in error_message:
                status = "Already in Radarr"
                logger.info(f"'{movie_folder}' folder already configured for an existing movie.")
            elif "Invalid Path" in error_message:
                status = "Invalid Path"
                logger.info(f"Path: {os.path.join(self.config.radarr_root_folder_path, movie_folder, '')} not valid.")
            elif "ID was not found" in error_message:
                status = "Invalid Movie ID"
                logger.info(f"ID: {tmdb_id} for '{movie_folder}' not correct")
            else:
                status = "Failed to Add"

            logger.error(f"Failed to add movie '{movie_title}' to Radarr: {error_message}")
            return {"result": "failure", "message": f"Failed to add movie: {error_message}", "status": status}

        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request error while adding movie to Radarr: {str(req_err)}")
            return {"result": "error", "message": f"Request error: {str(req_err)}"}

        except Exception as e:
            logger.error(f"Unexpected error while adding movie to Radarr: {str(e)}")
            return {"result": "error", "message": f"Unexpected error: {str(e)}"}
