from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel

# SQLAlchemy 엔진 생성

# 엔진은 SQLAlchemy와 데이터베이스 연결을 관리하는 객체
# DB 연결정보, SQLAlchemy가 SQl 쿼리를 데이타베이스에 전달하고 결과를 받아오는 역할

# connect_args={"check_same_thread": False}는 SQLite 데이터베이스와의 연결 설정 중 하나로,
# 현재 스레드에서만 사용 가능하도록 설정
# create_engine은 커넥션 풀을 생성 => 데이터베이스 접속하는 객체를 일정수만큼만들어
# 돌려쓰는 방식으로 세션접속에 소요되는 시간 단축, 데이터베이스에 동시접속수 제어


# 루트폴더에 저장
SQLALCHEMY_DATABASE_URL = "sqlite:///./Server_lecture/DB/section4_1DB.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 세션 DB 트랜잭션 관리하는 객체
# 세션을 통해 DB와 상호작용. 트랜잭션 단위처리
# 변경사항 커밋 롤백
# SessionLocal은 세션객체를 생성하는 팩토리함수 생성
# 이 팩토리를 통해 실제 세션객체를 생성

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SessionLocal은 세션객체 생성 팩토리함수
# SessionLocal() 호출하면 새로운 세션객체 생성
# 세선-> 데이타 베이스 상호작용 캡슐화,쿼리 실행, DB 추가,수정,삭제 작업관리

# 엔진 -> DB 연결설정(커넥션풀) 유지
# 세션 -> 트랜잭션단위로 DB 상호작용 DB 작업관리


# autocommit=False -> commit을 해야 변경사항 저장. 잘못저장되어도 rollback으로 취소가능
# SQLAlchemy 모델을 정의할 때 사용되는 베이스 클래스
Base = declarative_base()
# ORM에서 DB 테이블과 매핑되는 클래스의 베이스 클래스 생성


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Integer)


# SQLAlchemy는 Base 클래스를 상속받은 모든 클래스의 메타데이터를 참조하여 데이터베이스 테이블을 생성
# 메타데이터는 테이블 정의, 컬럼 정보, 데이터 타입, 인덱스 등 데이터베이스 테이블 구조를 설명하는 정보
Base.metadata.create_all(bind=engine)

# 입출력모델
# 입출력 모델을 사용하여 데이터베이스 모델에서 특정 필드를 숨기거나 변환할 수 있습니다.
# 예를 들어, 비밀번호 같은 민감한 정보는 응답에서 제외하거나, 다른 형식으로 반환할 수 있습니다.
# 이는 데이터베이스 모델을 그대로 클라이언트에 노출하는 것보다 더 안전합니다.

# API 인터페이스가 변경될 때, 입출력 모델을 수정하여 클라이언트와의 데이터 교환 형식을 쉽게 조정할 수 있습니다.
# 데이타베이스 모델을 변경하기는 매우 어려움


class ItemCreate(BaseModel):
    name: str
    description: str
    price: int


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
    price: int


# 호출될때마다 새로운 세션을 생성하고 finally에서 세션을 닫아버림
# 리소스 누수를 방지하고 세션이 정리되게 보장
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 제너레이터에서는 차례대로 결과를 반환하고자 return 대신 yield 키워드를 사용한다.
# 프로젝트 루트에 저장
