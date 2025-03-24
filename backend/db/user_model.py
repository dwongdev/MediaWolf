from db.base import Base
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String


class Users(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")

    def as_dict(self):
        return {"id": self.id, "name": self.name, "role": self.role}

    def get_id(self):
        return str(self.id)
