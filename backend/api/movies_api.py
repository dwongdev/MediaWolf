import urllib.parse

from db.movie_db_handler import MovieDBHandler
from flask import Blueprint, render_template
from flask_socketio import SocketIO
from services.radarr_services import RadarrService
from services.tmdb_services import TMDBService

movies_bp = Blueprint("movies", __name__)


class MoviesAPI:
    def __init__(self, db: MovieDBHandler, socketio: SocketIO, radarr_service: RadarrService, tmdb_service: TMDBService):
        self.db = db
        self.socketio = socketio
        self.radarr_service = radarr_service
        self.tmdb_service = tmdb_service
        self.recommended_movies = []

        self.setup_routes()
        self.setup_socket_events()

    def setup_routes(self):
        """Define Flask routes."""

        @movies_bp.route("/movies")
        def serve_movies_page():
            movie_items_in_db = self.db.get_existing_db_movies()
            movies_for_selection = {movie["title"].lower() for movie in movie_items_in_db}
            sorted_movies = [movie.title() for movie in sorted(movies_for_selection)]
            return render_template("movies.html", movies=sorted_movies)

    def setup_socket_events(self):
        """Handle Socket.IO events."""

        @self.socketio.on("load_movie_recommendations")
        def handle_load_recommendations():
            self.socketio.emit("movie_recommendations", {"data": self.db.recommended_movies})

        @self.socketio.on("refresh_movie_recommendations")
        def handle_refresh_movie_recommendations(data):
            recommended_movies = self.db.refresh_recommendations(data)
            if not len(recommended_movies):
                self.socketio.emit("new_toast_msg", {"title": "No movies found", "message": "Check logs for more info"})

            self.socketio.emit("movie_recommendations", {"data": recommended_movies})

        @self.socketio.on("add_movie_to_radarr")
        def handle_add_movie_to_radarr(movie_title, movie_year, tmdb_id):
            parsed_movie_title = urllib.parse.unquote(movie_title)
            return_result = self.radarr_service.add_movie_to_radarr(parsed_movie_title, tmdb_id)
            parsed_result = {"title": f"{parsed_movie_title} - {movie_year}", "status": return_result.get("status")}
            self.socketio.emit("refresh_movie", parsed_result)
            if return_result.get("result") != "success":
                self.socketio.emit("new_toast_msg", {"title": "Failed to add Movie", "message": return_result.get("message")})

        @self.socketio.on("dismiss_movie")
        def handle_dismiss_movie(movie_title):
            parsed_movie_title = urllib.parse.unquote(movie_title)
            self.db.dismiss_movie(parsed_movie_title)

        @self.socketio.on("movie_search")
        def handle_movie_search(data):
            query = data.get("query")
            if not query:
                self.socketio.emit("toast", {"title": "Blank Search Query", "body": "Please enter search request"})
                parsed_results = {}
            else:
                parsed_results = self.tmdb_service.perform_movie_search(query)
            self.socketio.emit("movie_search_results", {"results": parsed_results})

    def get_blueprint(self):
        return movies_bp
