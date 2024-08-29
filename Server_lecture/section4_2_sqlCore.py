from fastapi import FastAPI
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    select,
    insert,
    update,
    delete,
    func,
)

# 데이타 베이스 테이블 생성

# 엔진을 만들때는 반드시 db를 연결한다 없으면 생성
engine = create_engine("sqlite:///./Server_lecture/DB/section4_2sqlCore1.db", echo=True)
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
# 데이터 조회
try:
    with engine.connect() as conn:
        # select문 users 테이블
        result = conn.execute(select(users))
        # 모든 행
        rows = result.fetchall()
        # 모든행 출력
        for row in rows:
            print(row)
except Exception as e:
    print(f"Error: {e}")

# 데이타 삽입
with engine.connect() as conn:
    conn.execute(insert(users).values(name="John", age=18))
    conn.execute(
        insert(users).values([{"name": "Jack", "age": 22}, {"name": "Jack", "age": 22}])
    )
    conn.commit()

# 데이타 업데이트
with engine.connect() as conn:
    # users.c.name users의 name  column
    conn.execute(update(users).where(users.c.name == "John").values(age=22))
    conn.commit()

# 데이타 삭제
with engine.connect() as conn:
    conn.execute(delete(users).where(users.c.name == "Jack"))
    conn.commit()

from sqlalchemy import func

# 연령그룹별 평균계산, 이름정렬

try:
    with engine.connect() as conn:
        # select 쿼리를 만듬 execute 쿼리를 실행
        age_group_query = (
            select(users.c.name, func.avg(users.c.age).label("avg_age"))
            .group_by(users.c.name)
            .order_by(users.c.name)
        )
        result = conn.execute(age_group_query)
        for row in result:
            print(row)
except Exception as e:
    print(f"Error: {e}")
