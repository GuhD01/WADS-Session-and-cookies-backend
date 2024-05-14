from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    # Define user table columns
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    username = Column(String)
    hashed_password = Column(String)
    session_id = Column(Text, nullable=True)  # nullable because it's not always set

    # Establish a relationship between users and todos
    todos = relationship("Todo", back_populates="owner")


class Todo(Base):
    __tablename__ = "todos"

    # Define todo table columns
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Establish a relationship between todos and users
    owner = relationship("User", back_populates="todos")
