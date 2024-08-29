# 5 유효성검사 , 유효성 에러검출

from pydantic import BaseModel, ValidationError, field_validator


class User(BaseModel):
    name: str
    age: int

    # 나이 검증
    @field_validator("age")
    def check_age(cls, v):
        if v < 18:
            raise ValueError("No Teenager")
        return v


def process_user(user: User):
    # 데이터 처리
    return f"Name: {user.name} Age: {user.age}"


# 유효한 데이터

user_data = {"name": "John", "age": 20}
user = User(**user_data)  # 딕션어리를 풀어서 class에 넣어서 객체생성
print(f"객체모델출력\n{user}")
print(f"변환출력\n{process_user(user)}\n")

# 유효하지 않은 데이터

invalid_user_data = {"name": "John", "age": "twenty"}
# 데이타 타입이 안맞음
try:
    invalid_user = User(**invalid_user_data)
    print(f"모델출력\n{invalid_user}")
    print(process_user(invalid_user))
except ValidationError as e:
    print(f"Validation Error: {e}")
