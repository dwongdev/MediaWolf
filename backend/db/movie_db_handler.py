import urllib.parse

from db.database_handler import DatabaseHandler
from db.movie_models import DismissedMovie, RadarrMovie, RecommendedMovie
from logger import logger
from sqlalchemy import func


class MovieDBHandler(DatabaseHandler):
    def __init__(self):
        super().__init__()
        self.recommended_movies = []

    def get_existing_db_movies(self):
        """Retrieve all movie data from the database."""
        movies = {}
        try:
            session = self.SessionLocal()
            movies = [movie.as_dict() for movie in session.query(RadarrMovie).all()]
            session.close()

        except Exception as e:
            logger.error(f"Error Getting Existing DB Movies: {str(e)}")

        finally:
            return movies

    def add_radarr_movies(self, radarr_movies):
        try:
            """Add new movies from Radarr if they are not already in the database."""
            movie_items_in_db = self.get_existing_db_movies()
            movies_in_db = {movie["title"].lower() for movie in movie_items_in_db}
            new_movies_count = 0

            for movie in radarr_movies:
                movie_title = movie["title"].strip().lower()
                if movie_title not in movies_in_db:
                    movie_data = {
                        "title": movie["title"].strip(),
                        "genres": ", ".join(str(item) for item in movie.get("genres", [])),
                        "tmdb_id": movie.get("tmdbId", 0),
                    }
                    self.store_movie(movie_data)
                    new_movies_count += 1
                else:
                    logger.debug(f"Skipping existing movie: {movie_title}")

            logger.debug(f"Added {new_movies_count} new movies.")

        except Exception as e:
            logger.error(f"Error Adding Radarr Movie to DB: {str(e)}")

    def store_movie(self, movie_data):
        """Add a new movie to the database."""
        session = self.SessionLocal()
        try:
            movie = RadarrMovie(**movie_data)
            session.add(movie)
            session.commit()
            logger.info(f"Added movie: {movie_data['title']}")

        except Exception as e:
            logger.error(f"Error Storing Movie: {str(e)}")
            session.rollback()

        finally:
            session.close()

    def store_recommended_movies_for_radarr_movie(self, radarr_movie_title, recommended_movies):
        """Store recommended movies for a given Radarr movie."""
        try:
            session = self.SessionLocal()

            radarr_movie = session.query(RadarrMovie).filter(func.lower(RadarrMovie.title) == radarr_movie_title.lower()).first()

            if radarr_movie:
                new_recommended_count = 0

                movie_items_in_db = self.get_existing_db_movies()
                movies_in_db = {movie["title"].lower() for movie in movie_items_in_db}

                for recommended_item in recommended_movies:
                    try:
                        recommended_title = recommended_item["title"].strip()

                        if recommended_title.lower() in movies_in_db:
                            logger.info(f"Movie: {recommended_title} already in Radarr")
                        else:
                            recommended_movie = RecommendedMovie(**recommended_item)
                            session.add(recommended_movie)
                            new_recommended_count += 1
                            logger.info(f"Added recommended movie: {recommended_title}")

                            radarr_movie.recommended_movies.append(recommended_movie)

                    except Exception as e:
                        logger.error(f"Error Processing Recomendation: {recommended_title} {str(e)}")

                session.commit()
                logger.debug(f"Added {new_recommended_count} new recommended movies for {radarr_movie_title}.")
            else:
                logger.error(f"RadarrMovie {radarr_movie_title} not found in the database.")

        except Exception as e:
            logger.error(f"Error Getting Recommended Movies: {str(e)}")

        finally:
            session.close()

    def refresh_recommendations(self, data):
        """Retrieve movie recommendations based on filters."""
        selected_movie = data.get("selected_movie", "all").lower()
        min_popularity = data.get("min_popularity", None)
        min_vote_average = data.get("min_vote_average", None)
        sort_by = data.get("sort_by", "random")
        num_results = data.get("num_results", 10)
        page = data.get("page", 1)

        if selected_movie == "all":
            db_results = self._get_random_movies(min_popularity, min_vote_average, sort_by, num_results, page)
        else:
            db_results = self._get_recommended_movies_for_radarr_movie(selected_movie, min_popularity, min_vote_average, sort_by)

        json_results = [movie.as_dict() for movie in db_results]
        self.recommended_movies = json_results
        return json_results

    def _get_recommended_movies_for_radarr_movie(self, radarr_movie_title, min_popularity=None, min_vote_average=None, sort_by="popularity"):
        """Retrieve all recommended movies for a given Radarr movie, with optional filtering."""
        session = self.SessionLocal()
        try:
            logger.debug(f"Getting recommended movies for: {radarr_movie_title}")
            radarr_movie = session.query(RadarrMovie).filter(func.lower(RadarrMovie.title) == radarr_movie_title.lower()).first()

            if radarr_movie:
                recommended_movies_query = session.query(RecommendedMovie).filter(RecommendedMovie.radarr_movie_id == radarr_movie.id, ~RecommendedMovie.title.in_(session.query(DismissedMovie.title)))

                if min_popularity:
                    recommended_movies_query = recommended_movies_query.filter(RecommendedMovie.popularity >= min_popularity)
                if min_vote_average:
                    recommended_movies_query = recommended_movies_query.filter(RecommendedMovie.vote_average >= min_vote_average)

                recommended_movies_query = self._apply_sorting(recommended_movies_query, sort_by)
                recommended_movies = recommended_movies_query.all()

                logger.debug(f"Found {len(recommended_movies)} stored recommendations for: {radarr_movie_title}")
                return recommended_movies

            else:
                logger.error(f"RadarrMovie {radarr_movie_title} not found.")
                return []

        except Exception as e:
            logger.error(f"Error getting recommendations for {radarr_movie_title}: {str(e)}")
            return []

        finally:
            session.close()

    def _get_random_movies(self, min_popularity=None, min_vote_average=None, sort_by="popularity", num_results=10, page=1):
        """Retrieve random movies with filters, sorting, and pagination."""
        session = self.SessionLocal()
        try:
            query = session.query(RecommendedMovie).filter(~RecommendedMovie.title.in_(session.query(DismissedMovie.title)))

            if min_popularity:
                query = query.filter(RecommendedMovie.popularity >= min_popularity)
            if min_vote_average:
                query = query.filter(RecommendedMovie.vote_average >= min_vote_average)

            query = self._apply_sorting(query, sort_by)

            query = query.group_by(RecommendedMovie.title)

            offset = (page - 1) * num_results
            query = query.offset(offset).limit(num_results)

            movies = query.all()

            logger.debug(f"Page {page}: Retrieved {len(movies)} movies sorted by {sort_by}")
            return movies

        except Exception as e:
            logger.error(f"Error retrieving random movies: {str(e)}")
            return []

        finally:
            session.close()

    def _apply_sorting(self, query, sort_by):
        """Apply sorting based on the selected criteria."""
        if sort_by == "random":
            return query.order_by(func.random())
        elif sort_by == "pop-desc":
            return query.order_by(RecommendedMovie.popularity.desc())
        elif sort_by == "pop-asc":
            return query.order_by(RecommendedMovie.popularity.asc())
        elif sort_by == "average-vote-desc":
            return query.order_by(RecommendedMovie.vote_average.desc())
        elif sort_by == "average-vote-asc":
            return query.order_by(RecommendedMovie.vote_average.asc())
        else:
            return query

    def update_status_for_recommended_movie(self, movie_title, status):
        """Update the status of all recommended movies for a given movie title."""
        try:
            session = self.SessionLocal()

            recommended_movies = session.query(RecommendedMovie).filter(func.lower(RecommendedMovie.title) == movie_title.lower()).all()

            if recommended_movies:
                for recommended_movie in recommended_movies:
                    recommended_movie.status = status

                session.commit()
                logger.info(f"Updated status for {len(recommended_movies)} recommended movies with title '{movie_title}' to '{status}'.")

            for rec in self.recommended_movies:
                if rec.get("title", "").lower() == movie_title.lower():
                    rec["status"] = status

            else:
                logger.info(f"No recommended movies found for title '{movie_title}'.")

        except Exception as e:
            logger.error(f"Error updating status for recommended movie '{movie_title}': {str(e)}")

        finally:
            session.close()

    def dismiss_movie(self, raw_movie_title):
        """Mark an movie as dismissed by adding to the dismissed table."""
        session = self.get_session()
        try:
            movie_title = urllib.parse.unquote(raw_movie_title)
            existing_dismissed = session.query(DismissedMovie).filter(func.lower(DismissedMovie.title) == movie_title.lower()).first()

            if not existing_dismissed:
                dismissed_movie = DismissedMovie(title=movie_title)
                session.add(dismissed_movie)
                session.commit()
                logger.info(f"Dismissed movie: {movie_title}")
            else:
                logger.info(f"Movie '{movie_title}' is already dismissed.")

            self.recommended_movies = [movie for movie in self.recommended_movies if movie.get("title", "").lower() != movie_title.lower()]

        except Exception as e:
            logger.error(f"Error dismissing movie: {str(e)}")
            session.rollback()

        finally:
            session.close()
