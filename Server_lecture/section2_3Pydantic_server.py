from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class UserInput(BaseModel):
    name: str  # 필수필드
    age: int


# 입력을 받아 하나 추가해서 응답
class UserResponse(BaseModel):
    name: str
    age: int
    is_adult: bool


@app.post("/user/", response_model=UserResponse)
def create_user(user: UserInput):
    # typehint 로 모든  검사기능수행
    # 요청본문 request body로 들어온 데이터를 UserInput 모델로 파싱
    is_adult = user.age >= 18
    # 응답데이타를 구성
    reponse_data = UserResponse(name=user.name, age=user.age, is_adult=is_adult)
    return reponse_data
