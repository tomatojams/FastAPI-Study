from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel


class SuccessModel(BaseModel):
    message: str


class NotFountModel(BaseModel):
    error: str


class ValidationModel(BaseModel):
    error: list


app = FastAPI()


@app.get("/item/{item_id}", response_model=SuccessModel)
async def read_item(item_id: int):
    if item_id == 0:

        # 데이터베이스 조회등의 로직
        raise HTTPException(status_code=404, detail="Item not found")
    # 특정모델에 특정 메세지를 넣어서 반환가능
    return SuccessModel(message="Item found")


# HTTP 에러가 나면 실행
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    if exc.status_code == 404:
        return NotFountModel(error=exc.detail)
    elif exc.status_code == 422:
        return ValidationModel(error=exc.detail)
