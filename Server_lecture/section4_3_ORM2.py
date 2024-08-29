from fastapi import FastAPI
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    func,
    Table,
    Text,
    event,
)
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    relationship,
    joinedload,
    selectinload,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.hybrid import hybrid_property

# DATABASE_URL = "sqlite:///:memory:"  # In-memory DB
DATABASE_URL = "sqlite:///./Server_lecture/DB/section4_3ORM_2.db"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# 모델정의


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    addresses = relationship("Address", back_populates="user")
    roles = relationship("Role", secondary="association", back_populates="users")


class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True)
    email = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="addresses")


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    users = relationship("User", secondary="association", back_populates="roles")


association_table = Table(
    "association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role_id", Integer, ForeignKey("roles.id")),
)

# 하드브리드 속성 예제


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)

    # 파이썬 코드용
    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    # SQL expression 에서 ORM만으로 부족할때
    @full_name.expression
    def full_name(cls):
        # SQLite용
        return cls.first_name + " " + cls.last_name  # SQLite에서는 || 대신 + 사용


Base.metadata.create_all(engine)


# DB 파일을 생성하려면 app 생성해야함
# FastAPI가 초기화 작업을 해줌.


app = FastAPI()
# 데이타 추가 및 쿼리
# 서버코드에서 바로 실행해서 입출력용 모델 불필요

# SQLAlchemy는 primary 키가 integer형이면 자동으로 관리함 자동증가처리
user = User(name="John Doe")
address1 = Address(email="john@example.com", user=user)
address2 = Address(email="doe@example.com", user=user)

# 여러 테이블을 리스트로 묶어서 추가가능
session.add_all([user, address1, address2])
session.commit()


for address in session.query(Address).join(User).filter(user.name == "John Doe"):
    print(address.email)

# options - 제어항목-> joinedload: 조인되었을때 함께 로드함-> 데이타가 커질수있음
users = session.query(User).options(joinedload(User.addresses)).all()
for user in users:
    print(user.name)
    for address in user.addresses:
        print(address.email)


# 이벤트 리스너 SQLAlchemy의 기능
# 새로운 상용자가 등록될때마다 출력
@event.listens_for(Employee, "before_insert")
def my_listener(mapper, connection, target):
    print(f"New user created: {target.full_name}")


# 새 사용자 추가

new_user = User(name="tomatojams")
session.add(new_user)
session.commit()

all_users = session.query(User).all()
for user in all_users:
    print(user.name)

# 잘못된 예시
# 관계 필드에는 직접 값을 대입할 수 없다
# address_selected = session.query(Address).filter_by(user="John").one()
# print(address_selected)

# 관계필드는 부모테이블에서 찾아서 적용 first로 찾아야함
user = session.query(User).filter_by(name="John Doe").first()

address_selected = session.query(Address).filter_by(user_id=user.id).all()
for address in address_selected:
    print(address.email)

# 트랜잭션 관리

try:
    session.add(User(name="tomatojams"))  # 예시데이타 추가
    session.commit()
except SQLAlchemyError as e:
    session.rollback()
    print(f"Tracsaction failed: {e}")
finally:
    session.close()

# joinedload 와 selectedload 사용예

user_with_addresses_joined = (
    session.query(User).join(Address).options(joinedload(User.addresses)).all()
)
user_with_addresses_selected = (
    session.query(User).join(Address).options(selectinload(User.addresses)).all()
)

for user in user_with_addresses_selected:
    print("selected")
    print(user.name, [address.email for address in user.addresses])
for user in user_with_addresses_joined:
    print("joined")
    print(user.name, [address.email for address in user.addresses])

# 쿼리예제

session.add_all(
    [
        Employee(first_name="John", last_name="Doe"),
        Employee(first_name="Jane", last_name="Doe"),
    ]
)
session.commit()

for employee in session.query(Employee).filter(Employee.full_name == "John Doe"):
    print(employee.first_name, employee.last_name)
