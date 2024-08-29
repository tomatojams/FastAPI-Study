from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr, ValidationError
import sqlite3
from .SQL_ex_db import get_db, init_db

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: EmailStr  # Email 검증 추가

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True  # orm_mode 대신 from_attributes 사용

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    # 중복 이메일 확인
    cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
    existing_user = cursor.fetchone()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (user.name, user.email)
        )
        db.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=500, detail="Database integrity error")

    user_id = cursor.lastrowid
    cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
    db_user = cursor.fetchone()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(id=db_user[0], name=db_user[1], email=db_user[2])

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
    db_user = cursor.fetchone()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(id=db_user[0], name=db_user[1], email=db_user[2])

@app.get("/users/", response_model=list[UserResponse])
def read_users(skip: int = 0, limit: int = 10, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id, name, email FROM users LIMIT ? OFFSET ?", (limit, skip))
    users = cursor.fetchall()
    return [UserResponse(id=user[0], name=user[1], email=user[2]) for user in users]
