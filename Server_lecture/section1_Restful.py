import logging
from fastapi import FastAPI, Form
from typing import List,TypeVar, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

state = {"state": "connected"}
items = {'1': {"name":"codnnected"}, '2': {"name":"Pencil"}}

@app.get("/state")
async def get_state():
    return state

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items")
async def read_items():
    logger.info("Fetching all items")
    return items

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.post("/items/{item_id}")
async def create_item(item_id: str, name: str = Form(...)):
    logger.info(f"item created: {item_id}-{name}")
    items[item_id] = {"name": name}
    return items[item_id]

@app.put("/items/{item_id}")
async def udate_item( item_id: str, name: str = Form(...)):
    items[item_id] = {"name": name}
    logger.info(f"item updated: {item_id}-{name}")
    return items[item_id]

@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    if item_id in items:
        logger.info(f"item deleted: {item_id}")
        del items[item_id]
        return {"message": "Item deleted"}
    else:
        logger.info(f"item not found: {item_id}")
        return {"message": "Item not found"}

@app.patch("/items/{item_id}")
async def patch_item(item_id: str, name: str = Form(...)):
    if item_id in items:
        items[item_id]["name"] = name
        logger.info(f"item updated: {item_id}-{name}")
        return items[item_id]
    else:
        logger.info(f"item not found: {item_id}")
        return {"message": "Item not found"}

#2. 쿼리 매개변수 'skip'과 'limit'을 사용
# /items/?skip=0&limit=10
@app.get("/items/")
async def read_items(skip:int = 0, limit:int = 10):
    return {"skip": skip, "limit": limit}

#2. 쿼리 매개변수 'q'를 사용
# /items/?q=foo?q=bar
@app.get("/items/")
async def read_items(q: List[str] = None):
    return {"q": q}

# 3. 요청본문 파라미터방식-data 전송
from fastapi import Request

@app.post("/items")
async def create_item(request:Request):
    data = await request.json()
    # data 는 파이썬 딕셔너리입니다.
    return data

# 4. 폼데이터
from fastapi import Form

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username, "password": password}

# 5. 헤더 매개변수
from fastapi import Header
# Header 클래스 사용 매개변수 받아 Pythonic한 방식으로 자동변환

@app.get("/items/")
async def read_items(user_agent: str = Header(None)):
    return {"User-Agent": user_agent}

# 6. 쿠키 매개변수

from fastapi import Cookie

@app.get("/items/")
async def read_items(ads_id: str = Cookie(None)):
    return {"ads_id": ads_id}


    # if __name__ == "__main__":
    #     import uvicorn
    #     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

