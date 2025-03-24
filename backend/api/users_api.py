from flask import Blueprint, render_template
from flask_socketio import SocketIO
from services.user_services import UserService

users_bp = Blueprint("users", __name__)


class UsersAPI:
    def __init__(self, user_service: UserService, socketio: SocketIO):
        self.socketio = socketio
        self.users = user_service

        self.setup_routes()
        self.setup_socket_events()

    def setup_routes(self):
        """Define Flask Routes."""

        @users_bp.route("/users")
        def serve_user_page():
            return render_template("users.html")

    def setup_socket_events(self):
        @self.socketio.on("get_users")
        def get_users():
            """Send all users to the client (in case they manually refresh the list)."""
            try:
                users = self.users.get_all_users()
                self.socketio.emit("users_list", {"users": users})

            except Exception as e:
                self.socketio.emit("new_toast_msg", {"title": "Error", "message": f"Failed to fetch users: {str(e)}", "type": "error"})

        @self.socketio.on("save_user")
        def save_user(data):
            """Update user role or password and notify all clients."""
            user_id = data.get("id")
            try:
                user = self.users.get_user_by_id(user_id)
                if not user:
                    raise ValueError("User not found")

                self.users.update_user(data)
                self.socketio.emit("new_toast_msg", {"title": "Success", "message": f"User {user.name} updated successfully", "type": "success"})
                self.socketio.emit("user_updated")

            except Exception as e:
                self.socketio.emit("new_toast_msg", {"title": "Error", "message": f"Failed to update user: {str(e)}", "type": "error"})

        @self.socketio.on("create_user")
        def create_user(data):
            try:
                self.users.create_user(data)
                self.socketio.emit("new_toast_msg", {"title": "Success", "message": f"User {data.get('name')} created successfully", "type": "success"})
                self.socketio.emit("user_created")

            except Exception as e:
                self.socketio.emit("new_toast_msg", {"title": "Error", "message": f"Failed to create user: {str(e)}", "type": "error"})

        @self.socketio.on("delete_user")
        def delete_user(data):
            try:
                user_id = data.get("id")
                self.users.delete_user(user_id)
                self.socketio.emit("new_toast_msg", {"title": "Success", "message": f"User {data.get('name')} deleted successfully", "type": "success"})
                self.socketio.emit("user_deleted")

            except Exception as e:
                self.socketio.emit("new_toast_msg", {"title": "Error", "message": f"Failed to delete user: {str(e)}", "type": "error"})

    def get_blueprint(self):
        return users_bp
