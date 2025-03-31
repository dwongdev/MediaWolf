from db.database_handler import DatabaseHandler
from flask import Blueprint, render_template
from flask_socketio import SocketIO
from services.readarr_services import ReadarrService
from services.spotify_services import SpotifyService

audiobooks_bp = Blueprint("audiobooks", __name__)


class AudioBooksAPI:
    def __init__(self, db: DatabaseHandler, socketio: SocketIO, readarr_service: ReadarrService, spotify_service: SpotifyService):
        self.db = db
        self.socketio = socketio
        self.readarr_service = readarr_service
        self.spotify_service = spotify_service
        self.recommended_audiobooks = []

        self.setup_routes()
        self.setup_socket_events()

    def setup_routes(self):
        """Define Flask routes."""

        @audiobooks_bp.route("/audiobooks")
        def serve_audiobooks_page():
            return render_template("audiobooks.html")

    def setup_socket_events(self):
        """Handle Socket.IO events."""

        @self.socketio.on("audiobook_search")
        def handle_audiobook_search(query_req):
            if not query_req:
                self.socketio.emit("toast", {"title": "Blank Search Query", "body": "Please enter search request"})
                parsed_results = {}
            else:
                parsed_results = self.spotify_service.search_audiobooks(query_req)
            self.socketio.emit("audiobook_search_results", {"results": parsed_results})

        @self.socketio.on("refresh_audiobook_recommendations")
        def handle_refresh_audiobook_recommendations(data):
            pass

    def get_blueprint(self):
        return audiobooks_bp
