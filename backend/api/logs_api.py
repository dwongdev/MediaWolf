import threading

from flask import Blueprint, render_template
from flask_socketio import SocketIO
from services.config_services import LOG_FILE_NAME

logs_bp = Blueprint("logs", __name__)


class LogsAPI:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.logs = ""
        self.lock = threading.Lock()
        self.setup_routes()
        self.setup_socket_events()

    def read_logs(self):
        """Reads the entire log file and returns the content."""
        try:
            with open(LOG_FILE_NAME, "r") as log_file:
                return log_file.read()

        except Exception as e:
            return f"Error loading logs: {str(e)}"

    def fetch_logs_in_thread(self):
        """Fetch logs in a background thread."""
        logs_from_file = self.read_logs()
        with self.lock:
            self.logs = logs_from_file
        self.socketio.emit("refreshed_logs", self.logs)

    def setup_routes(self):
        """Define Flask routes."""

        @logs_bp.route("/logs")
        def serve_logs_page():
            return render_template("logs.html", logs=self.logs)

    def setup_socket_events(self):
        """Handle Socket.IO events."""

        @self.socketio.on("refresh_logs")
        def handle_refresh_logs():
            """Fetch logs in the background."""
            thread = threading.Thread(target=self.fetch_logs_in_thread, daemon=True)
            thread.start()

    def get_blueprint(self):
        return logs_bp
