import os
from datetime import timedelta

from api.books_api import BooksAPI
from api.downloads_api import DownloadsAPI
from api.logs_api import LogsAPI
from api.movies_api import MoviesAPI
from api.music_api import MusicAPI
from api.settings_api import SettingsAPI
from api.shows_api import ShowsAPI
from api.subscriptions_api import SubscriptionsAPI
from api.tasks_api import TasksAPI
from api.users_api import UsersAPI
from db.movie_db_handler import MovieDBHandler
from db.music_db_handler import MusicDBHandler
from db.user_db_handler import UserDBHandler
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_socketio import SocketIO
from logger import logger
from services.config_services import Config
from services.lidarr_services import LidarrService
from services.radarr_services import RadarrService
from services.readarr_services import ReadarrService
from services.sonarr_services import SonarrService
from services.spotdl_download_services import SpotDLDownloadService
from services.spotify_services import SpotifyService
from services.tmdb_services import TMDBService
from services.user_services import UserService


class MediaWolfApp:
    def __init__(self, host="0.0.0.0", port=5000):
        self.spotdl_download_history = {}
        self.host = host
        self.port = port

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        template_path = os.path.join(base_dir, os.path.join("frontend", "templates"))
        static_path = os.path.join(base_dir, os.path.join("frontend", "static"))

        self.app = Flask(__name__, template_folder=template_path, static_folder=static_path)
        self.app.secret_key = os.getenv("flask_secret_key", "secret_key")
        self.app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        self.music_db = MusicDBHandler()
        self.movies_db = MovieDBHandler()
        self.user_db = UserDBHandler()
        self.config = Config()
        self.lidarr_service = LidarrService(self.config, self.music_db)
        self.sonarr_service = SonarrService()
        self.radarr_service = RadarrService(self.config, self.movies_db)
        self.readarr_service = ReadarrService()
        self.spotdl_download_service = SpotDLDownloadService(self.config, self.spotdl_download_history)
        self.spotify_service = SpotifyService(self.config)
        self.tmdb_service = TMDBService(self.config)
        self.user_service = UserService()

        self.music_api = MusicAPI(self.music_db, self.socketio, self.lidarr_service, self.spotify_service, self.spotdl_download_service)
        self.books_api = BooksAPI(self.music_db, self.socketio, self.readarr_service)
        self.movies_api = MoviesAPI(self.movies_db, self.socketio, self.radarr_service, self.tmdb_service)
        self.shows_api = ShowsAPI(self.music_db, self.socketio, self.sonarr_service)
        self.downloads_api = DownloadsAPI(self.socketio)
        self.subscriptions_api = SubscriptionsAPI(self.socketio, self.config)
        self.settings_api = SettingsAPI(self.music_db, self.socketio, self.config)
        self.users_api = UsersAPI(self.user_service, self.socketio)
        self.tasks_api = TasksAPI(self.socketio, self.config, self.lidarr_service, self.radarr_service, self.readarr_service, self.sonarr_service)
        self.logs_api = LogsAPI(self.socketio)

        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)
        self.login_manager.login_view = "login"
        self.login_manager.user_loader(self.user_service.load_user)

        self.add_routes()
        self.setup_socket_events()

    def add_routes(self):
        """Define Flask routes."""
        self.app.register_blueprint(self.books_api.get_blueprint())
        self.app.register_blueprint(self.movies_api.get_blueprint())
        self.app.register_blueprint(self.shows_api.get_blueprint())
        self.app.register_blueprint(self.music_api.get_blueprint())
        self.app.register_blueprint(self.downloads_api.get_blueprint())
        self.app.register_blueprint(self.subscriptions_api.get_blueprint())
        self.app.register_blueprint(self.settings_api.get_blueprint())
        self.app.register_blueprint(self.tasks_api.get_blueprint())
        self.app.register_blueprint(self.logs_api.get_blueprint())
        self.app.register_blueprint(self.users_api.get_blueprint())

        @self.app.before_request
        def before_request():
            if not self.config.login_required:
                return
            if not current_user.is_authenticated:
                if request.endpoint not in ["login", "static"]:
                    return redirect(url_for("login"))

        @self.app.route("/")
        def home():
            artists_for_selection = self.music_db.get_existing_db_artists()
            sorted_artists = [artist.title() for artist in sorted(artists_for_selection)]
            return render_template("music.html", artists=sorted_artists)

        @self.app.route("/login", methods=["GET", "POST"])
        def login():
            if request.method == "POST":
                username = request.form["username"]
                password = request.form["password"]

                user = self.user_db.get_user_by_username(username)
                if user and self.user_service.authenticate_user(username, password):
                    login_user(user)
                    flash("Login successful", "success")
                    return redirect(url_for("home"))
                else:
                    flash("Invalid credentials", "danger")
            return render_template("login.html")

        @self.app.route("/logout")
        def logout():
            logout_user()
            flash("You have been logged out.", "info")
            return redirect(url_for("login"))

    def setup_socket_events(self):
        """Set up Socket.IO events."""

        @self.socketio.on("connect")
        def handle_connect():
            logger.info("Client connected")

        @self.socketio.on("disconnect")
        def handle_disconnect():
            logger.info("Client disconnected")

    def run(self):
        """Run Flask app with SocketIO."""
        self.socketio.run(self.app, host=self.host, port=self.port)

    def get_app(self):
        return self.app


media_wolf_app = MediaWolfApp()

if __name__ == "__main__":
    media_wolf_app.run()
else:
    app = media_wolf_app.get_app()
