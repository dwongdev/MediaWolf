from db.database_handler import DatabaseHandler
from db.user_model import Users
from logger import logger


class UserDBHandler(DatabaseHandler):
    def __init__(self):
        super().__init__()

    def get_existing_user(self):
        try:
            session = self.SessionLocal()
            users = [{"id": user.id, "name": user.name.lower(), "role": user.role.lower()} for user in session.query(Users.id, Users.name, Users.role).all()]
            session.close()
            return users

        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            raise

    def get_user_by_id(self, user_id):
        try:
            session = self.SessionLocal()
            user = session.query(Users).filter(Users.id == user_id).first()
            session.close()
            if not user:
                raise ValueError(f"User with ID {user_id} not found")
            return user

        except Exception as e:
            logger.error(f"Error fetching user by ID: {e}")
            raise

    def get_user_by_username(self, username):
        try:
            session = self.SessionLocal()
            user = session.query(Users).filter(Users.name == username).first()
            session.close()
            return user

        except Exception as e:
            logger.error(f"Error fetching user by username: {e}")
            raise

    def set_password(self, user_id, hashed_password):
        """Sets the password for a user. Assumes the password is already hashed."""
        try:
            session = self.SessionLocal()
            user = session.query(Users).filter(Users.id == user_id).first()

            if user:
                user.password = hashed_password
                session.commit()
            else:
                logger.warning(f"User with id {user_id} not found")

        except Exception as e:
            session.rollback()
            logger.error(f"Error setting password for user {user_id}: {str(e)}")

        finally:
            session.close()

    def update_user(self, user_id, updates):
        try:
            session = self.SessionLocal()
            user = session.query(Users).filter_by(id=user_id).first()
            if not user:
                raise ValueError(f"User with ID {user_id} not found")

            for key, value in updates.items():
                setattr(user, key, value)

            session.commit()
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating user: {e}")
            raise

        finally:
            session.close()

    def create_user(self, user):
        try:
            session = self.SessionLocal()
            new_user = Users(name=user.get("name").strip(), password=user.get("password"), role=user.get("role"))
            session.add(new_user)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error creating user: {e}")
            raise

        finally:
            session.close()

    def delete_user(self, user_id):
        try:
            session = self.SessionLocal()
            deleted_count = session.query(Users).filter(Users.id == user_id).delete()
            if deleted_count == 0:
                raise ValueError(f"User with ID {user_id} not found")
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting user: {e}")
            raise

        finally:
            session.close()
