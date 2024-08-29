# 동작안하는 더미코드

from fastapi import FastAPI
import httpx
import asyncio

app = FastAPI()


async def get_remote_data(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text


@app.get("/data/")
async def read_data():
    external_data = await get_remote_data(
        "https://jsonplaceholder.typicode.com/todos/1"
    )
    return external_data
