import bcrypt
from db.user_db_handler import UserDBHandler
from flask_login import current_user, login_user, logout_user
from logger import logger


class UserService:
    def __init__(self):
        self.user_db_handler = UserDBHandler()

    def _hash_password(self, password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def get_all_users(self):
        try:
            users = self.user_db_handler.get_existing_user()
            if users is None:
                raise ValueError("No users found")
            return users

        except Exception as e:
            logger.error(f"Failed to fetch users: {str(e)}")
            raise

    def get_user_by_id(self, user_id):
        try:
            user = self.user_db_handler.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"User with ID {user_id} not found")
            return user

        except Exception as e:
            logger.error(f"Failed to fetch user by ID: {str(e)}")
            raise

    def update_user(self, data):
        try:
            user_id = data.get("id")
            if not user_id:
                raise ValueError("User ID is missing")

            old_user_data = self.user_db_handler.get_user_by_id(user_id)
            if not old_user_data:
                raise ValueError(f"User with ID {user_id} not found")

            updates = {}
            for key, new_value in data.items():
                old_value = getattr(old_user_data, key, None)
                if key == "password" and new_value:
                    new_value = self._hash_password(new_value)

                if new_value != old_value:
                    updates[key] = new_value

            if updates:
                success = self.user_db_handler.update_user(user_id, updates)
                if not success:
                    raise Exception("Failed to update user in the database")

        except Exception as e:
            logger.error(f"Failed to update user: {str(e)}")
            raise

    def create_user(self, data):
        try:
            username = data.get("name")
            password = data.get("password")
            role = data.get("role")

            if not (username and password and role):
                raise ValueError("Missing user details")

            hashed_password = self._hash_password(password)
            new_user = {"name": username, "password": hashed_password, "role": role}
            success = self.user_db_handler.create_user(new_user)

            if not success:
                raise Exception("Failed to create user in the database")

        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise

    def delete_user(self, user_id):
        try:
            success = self.user_db_handler.delete_user(user_id)
            if not success:
                raise Exception("Failed to delete user")

        except Exception as e:
            logger.error(f"Failed to delete user: {str(e)}")
            raise

    def check_password(self, user, password):
        return bcrypt.checkpw(password.encode("utf-8"), user.password)

    def authenticate_user(self, username, password):
        user = self.user_db_handler.get_user_by_username(username)
        if user and self.check_password(user, password):
            return user
        return None

    def login_user(self, username, password):
        user = self.authenticate_user(username, password)
        if user:
            login_user(user)
            return user
        return None

    def logout_user(self):
        logout_user()

    def get_current_user(self):
        return current_user

    def load_user(self, user_id):
        user = self.get_user_by_id(user_id)
        return user
