from fastapi import FastAPI, HTTPException, Depends, Response
from typing import Optional, List
from . import crud, models, schemas
from .database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .utils import generate_session_id

app = FastAPI()

origins = [
    "http://localhost:5174",
    "localhost:5174",
    "http://localhost:5173",
    "localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.add_new_user(db=db, new_user=user)

@app.post("/login/")
def login_user(user: schemas.UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = crud.find_user_by_email(db, email=user.email)
    if db_user and db_user.hashed_password == user.password:
        session_id = generate_session_id()
        db_user.session_id = session_id
        db.commit()
        # Set cookie securely and httponly for production, adjust for local development
        response.set_cookie(key="session_id", value=session_id, httponly=True, secure=False, path='/')
        return JSONResponse(content={"success": True, "user_id": db_user.id, "session_id": session_id}, status_code=200)
    return JSONResponse(content={"success": False}, status_code=401)

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    return crud.find_user(db=db, user_id=user_id)

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.fetch_users(db=db, skip=skip, limit=limit)

@app.delete("/delete-users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return crud.remove_user(db=db, user_id=user_id)

@app.post("/users/{user_id}/todos/", response_model=schemas.Todo)
def create_todo(todo: schemas.TodoCreate, user_id: int, db: Session = Depends(get_db)):
    return crud.add_new_todo(db=db, new_todo=todo, user_id=user_id)

@app.get("/todos/{todo_id}", response_model=schemas.Todo)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    return crud.find_todo(db=db, todo_id=todo_id)

@app.get("/todos/", response_model=List[schemas.Todo])
def read_todos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.fetch_todos(db=db, skip=skip, limit=limit)

@app.put("/users/{user_id}/todos/{todo_id}", response_model=schemas.Todo)
def update_todo(todo_id: int, user_id: int, todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    return crud.modify_todo(db=db, user_id=user_id, todo_id=todo_id, updated_todo=todo)

@app.delete("/users/{user_id}/todos/{todo_id}")
def delete_todo(todo_id: int, user_id: int, db: Session = Depends(get_db)):
    return crud.remove_todo(db=db, user_id=user_id, todo_id=todo_id)

@app.get("/user/{user_id}/todos/", response_model=List[schemas.Todo])
def read_todos_by_user_id(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.fetch_todos_by_user_id(db=db, user_id=user_id, skip=skip, limit=limit)

@app.get("/user/{user_id}/todos/{todo_id}", response_model=schemas.Todo)
def read_todo_by_user_id_and_todo_id(user_id: int, todo_id: int, db: Session = Depends(get_db)):
    return crud.find_todo_by_user_id_and_todo_id(db=db, user_id=user_id, todo_id=todo_id)

@app.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    success = crud.delete_session(db=db, session_id=session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully."}