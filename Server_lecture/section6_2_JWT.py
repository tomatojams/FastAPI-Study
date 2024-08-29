from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordRequestForm,
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer,
)
from jose import jwt, JWTError
from pydantic import BaseModel
from datetime import timedelta, datetime
from typing import Optional

# JWT secret key
SECRET_KEY = "1234"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 유저 데이타베이스 시뮬레이션
fake_users_db = {
    "johnoe": {
        "username": "johnoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "hashedword",
        "disabled": False,
    }
}

# 유저모델


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


# 유저인 DB 모델
class UserInDB(User):
    hashed_password: str


# 토큰을 검증하는 객체
# 생성 url을 명시하고 검증객체는 생성
# Authorization  헤더 에서 토큰 추출하고 검증  하고 str형태로 돌려줌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app = FastAPI()


def fake_hash_password(password: str):
    return "hashed" + password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # data -> 토큰에 포함될, JWT 페이로드 , 사용자정보등을 담는다.
    to_encode = data.copy()
    # 만료시간
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    # 계산된 만료시간을 exp라는 키로 추가
    to_encode.update({"exp": expire})
    # json Web Token 생성 (사용자정보, JWT서명비밀키-서버만 알아야함, 암호화방식)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not fake_hash_password(password) == user.hashed_password:
        return False
    return user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
