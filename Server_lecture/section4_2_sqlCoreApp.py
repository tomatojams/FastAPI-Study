from typing import List
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.engine import Engine
from contextlib import contextmanager
from pydantic import BaseModel

# SQLAlchemy Core를 활용한 저수준 API를 써본다 제어가 상세, 최적화 가능
# 엔진, 커넥션 풀, SQL 표현언어, 스키마정의, 결과처리기 (execute)
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    select,
    delete,
    update,
    insert,
    func,
)

engine = create_engine("sqlite:///./Server_lecture/DB/section4_2sqlCore2.db", echo=True)
# echo sql문 콘솔출력
metadata = MetaData()
# 테이블을 만들기위한 데이타
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("age", Integer),
)

metadata.create_all(engine)
app = FastAPI()


class User(BaseModel):
    name: str
    age: int


class UserResponse(BaseModel):
    id: int
    name: str
    age: int


class UserUpdate(BaseModel):
    name: str = None  # 선택적 데이타
    age: int = None


class AverageAgeResponse(BaseModel):
    name: str
    average_age: float


# 직접 SQL문을 쓰는 방법


# from sqlalchemy import text
# @app.get('/users/{user_id}', response_model=List[UserResponse])
# def get_user(user_id:int, db:Engine = Depends(get_db)):
#     query = text("SELECT * FROM users WHERE id =: user_id")
#     result = db.execute(query,{"user_id":user_id})
#     item = result.fetchone()
#     if item:
#         return UserResponse(id=item[0],name=item[1],age=item[2])
#     raise HTTPException(status_code=404, detail="User not found")


# 쿼리처럼 활용하는 api
# SELECT * FROM users
@app.get("/users/", response_model=List[UserResponse])
def read_users():
    with engine.connect() as conn:
        results = conn.execute(select(users))
        user_list = results.fetchall()  # 전부 리스트로 가져옴
        return [UserResponse(id=row[0], name=row[1], age=row[2]) for row in user_list]


# INSERT INTO user(c1,c2,c3) VALUES (user_id,user.name,user.age)
@app.post("/users/", response_model=UserResponse)
def create_user(user: User):
    with engine.connect() as conn:
        result = conn.execute(insert(users).values(name=user.name, age=user.age))
        conn.commit()
        user_id = result.lastrowid
        return UserResponse(id=user_id, name=user.name, age=user.age)


# UPDATE user SET c1=?, c2=?, c3=? where c4=?
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate):
    print("start update")
    with engine.connect() as conn:
        update_stmt = update(users).where(users.c.id == user_id)
        if user.name:
            update_stmt = update_stmt.values(name=user.name)
        if user.age:
            update_stmt = update_stmt.values(age=user.age)
        conn.execute(update_stmt)
        conn.commit()
    print("end update")
    return read_user(user_id)


# SELECT * FROM user WHERE id= user_id
@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int):
    with engine.connect() as conn:
        result = conn.execute(select(users).where(users.c.id == user_id))
        user = result.fetchone()
        if user:  # 일치하는 값이 있으면
            return UserResponse(id=user[0], name=user[1], age=user[2])
        else:
            raise HTTPException(status_code=404, detail="User not found")


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    with engine.connect() as conn:
        conn.execute(delete(users).where(users.c.id == user_id))
        conn.commit()
    return {"message": "Deleted Successfully"}
