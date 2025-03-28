from db.database_handler import DatabaseHandler
from flask import Blueprint, render_template
from flask_socketio import SocketIO
from services.readarr_services import ReadarrService

audiobooks_bp = Blueprint("audiobooks", __name__)


class AudioBooksAPI:
    def __init__(self, db: DatabaseHandler, socketio: SocketIO, readarr_service: ReadarrService):
        self.db = db
        self.socketio = socketio
        self.readarr_service = readarr_service
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

        @self.socketio.on("refresh_audiobook_recommendations")
        def handle_refresh_audiobook_recommendations(data):
            pass

    def get_blueprint(self):
        return audiobooks_bp
