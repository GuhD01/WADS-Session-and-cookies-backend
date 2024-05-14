

from sqlalchemy.orm import Session
from . import models, schemas


def add_new_user(db: Session, new_user: schemas.UserCreate):
    db_user = models.User(email=new_user.email, username=new_user.username, hashed_password=new_user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def find_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def find_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def fetch_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()

def modify_user(db: Session, user_id: int, updated_user: schemas.UserCreate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        for key, value in updated_user.dict().items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def remove_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


def add_new_todo(db: Session, new_todo: schemas.TodoCreate, user_id: int):
    db_todo = models.Todo(**new_todo.dict(), user_id=user_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def find_todo(db: Session, todo_id: int):
    return db.query(models.Todo).filter(models.Todo.id == todo_id).first()

def fetch_todos(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Todo).offset(skip).limit(limit).all()

def modify_todo(db: Session, user_id: int, todo_id: int, updated_todo: schemas.TodoCreate):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.user_id == user_id).first()
    if db_todo:
        for key, value in updated_todo.dict().items():
            setattr(db_todo, key, value)
        db.commit()
        db.refresh(db_todo)
    return db_todo

def remove_todo(db: Session, user_id: int, todo_id: int):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.user_id == user_id).first()
    if db_todo:
        db.delete(db_todo)
        db.commit()
        return True
    return False

def fetch_todos_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.Todo).filter(models.Todo.user_id == user_id).offset(skip).limit(limit).all()

def find_todo_by_user_id_and_todo_id(db: Session, user_id: int, todo_id: int):
    return db.query(models.Todo).filter(models.Todo.user_id == user_id, models.Todo.id == todo_id).first()

def delete_session(db: Session, session_id: str):
    # Find the user with the given session_id
    user = db.query(models.User).filter(models.User.session_id == session_id).first()
    if not user:
        return False
    # Clear the session_id field
    user.session_id = None
    db.commit()
    return True