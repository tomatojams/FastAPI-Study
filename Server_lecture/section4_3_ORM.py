from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.sql import func

# 엔진설정
engine = create_engine(
    "sqlite:///./Server_lecture/DB/section4_3.db",
)
Session = sessionmaker(bind=engine)
session = Session()

# 모델 베이스 클래스
Base = declarative_base()

# 각 게시글은 단 하나의 사용자만 작성합니다. 이는 전형적인 일대다(1:N ) 관계입니다:
# User (부모 테이블) ↔ Post (자식 테이블)
# 한 사용자는 여러 게시글을 가질 수 있습니다.
# 한 게시글은 한 사용자에 의해 작성됩니다.


# 사용자 테이블 정의
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)

    # 자동업데이트 되는 칼럼
    # 부모테이블(users)에서 post객체를 리스트처럼 동작 back_populates 를 통해서
    # 글을 쓸때마다 Posts의 리스트는 업데이트됨
    # 리스트형식이라고 명시하지 않아도 알아서 해줌.

    posts = relationship("Post", back_populates="author")

    #  Post 객체의 author와 동기화된다.
    # 자동삭제까지 하고싶으면 아래옵션
    # posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User (name= {self.name}, age= {self.age})>"


# 게시글 테이블 정의 한명의 유저에게서 여러개의 포스트가 나올수있음
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    # ForeignKey를 통해서 1:n 관계임을 알수있음 왜냐면 이경우 한개의 useraks 가질수있고
    user_id = Column(Integer, ForeignKey("users.id"))

    # 자동동기화를 위해 설정
    # Post 객체가 어떤 User 객체에 속하는지 명시,
    author = relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<Post (title = {self.title}, content = {self.content})>"


def print_all_data(session):
    all_users = session.query(User).all()
    print("All_users:")
    for user in all_users:
        print(user)

    all_posts = session.query(Post).all()
    print("All_posts:")
    for post in all_posts:
        print(post)


# 테이블 생성

Base.metadata.create_all(engine)
print("Tables created.")
print_all_data(session)
app = FastAPI()
# 데이터 추가

new_user = User(name="John Doe", age=28)
new_post = Post(
    title="My first post",
    content="This is firts test post",
    author=new_user,
    # author에 관계가 맺어져있음
)
session.add(new_user)
session.add(new_post)
session.commit()
print("Added new user and post.", new_user, new_post)
print_all_data(session)

"""

filter: SQL 표현식 사용
filter_by: 키워드 인자 방식

filter를 사용한 예제:

user = session.query(User).filter(User.name == "John Doe").first()
여기서 User.name == "John Doe"는 SQL 표현식으로, name 필드가 "John Doe"인 사용자 하나를 찾습니다.

filter_by를 사용한 예제:

user = session.query(User).filter_by(name="John Doe").first()
여기서는 filter_by 메서드를 사용하여 name이 "John Doe"인 사용자 하나를 찾습니다.

유연성:

filter는 더 복잡한 쿼리 조건을 작성할 수 있어 복잡한 필터링 작업에 적합합니다.
filter_by는 간단하고 직관적인 조건을 작성할 때 유용합니다.

"""

# 데이타 조회
# filter는 "조건"을 "SQL 표현식"으로 직접 작성  where User.age > 20
users = session.query(User).filter(User.age > 20).all()
print("Users older than 20:", users)
print_all_data(session)


# 데이타수정
# filter_by는 키워드 인자방식 User모델의 속성이름을 직접 사용(전달받은 인자)


# 데이타베이스의 내용자체를 객체로 받아옴 따라서 그걸 바로 수정 삭제가능
user = session.query(User).filter_by(name="John Doe").first()
# 객체로 다루기때문에 별도의 SQL문을 쓰지 않아도 수정가능
if user:
    user.age = 30
    session.commit()
    print("Updated user and post.", user)
    print_all_data(session)

# 데이타 삭제
# 객체로 다루기때문에 별도의 SQL문을 쓰지 않아도 삭제가능
# session.delete(new_post)
# session.commit()
# print("Deleted user and post.", new_post)
# print_all_data(session)

# 복합쿼리
users_with_posts = (
    session.query(User).join(Post).filter(Post.content.like("%test%")).all()
)
print("Users with post containg 'test':", users_with_posts)
print_all_data(session)
