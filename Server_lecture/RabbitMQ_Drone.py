## 패키지 설치시 P.Tmind 미들웨어가 깨지기때문에 다른 환경에서

import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from aio_pika import connect_robust, IncomingMessage, Message, DeliveryMode
from typing import List
from dotenv import load_dotenv

# ObjectId 타입을 문자열로 변환해주는 유틸리티 함수
# bson은 절대로 따로 깔지말고 mongoengine에 포함된걸 써야함 그냥 깔면 에러남
from bson import ObjectId

load_dotenv()


app = FastAPI()

# MongoDB 연결 설정
mongo_url = os.getenv("MONGODB_LOCAL_URL")
client = AsyncIOMotorClient(mongo_url)
db = client["drone_db"]
collection = db["server_message"]

# 메시지를 버퍼로 임시 저장할 메모리 기반의 큐
BUFFER_SIZE = 30
message_buffer = []

# 클라이언트 요청을 위한 드론 목록
tracked_drones = set()


class Drone(BaseModel):
    name: str = Field(default=None)
    frequency: float = Field(default=None)
    bandwidth: float = Field(default=None)
    allow_track: bool = Field(default=None)
    allow_takeover: bool = Field(default=None)
    class_name: str = Field(default=None)
    radio_resources: int = Field(default=None)
    droneId: str = Field(default=None)
    latitude: float = Field(default=None)
    longitude: float = Field(default=None)


class DroneMessage(BaseModel):
    message: str = Field(..., enum=["FOUND", "WARNING", "ERROR", "VERIFY", "TEST"])
    sender_id: str
    drone: Drone


async def save_to_db(drone_message_content: dict):
    result = await collection.insert_one(drone_message_content)
    return result.inserted_id


# ObjectId를 문자열로 변환하는 함수
def object_id_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, dict):
        return {k: object_id_to_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [object_id_to_str(v) for v in obj]
    return obj


async def process_message(message: IncomingMessage):
    async with message.process():
        try:
            drone_message_content = json.loads(message.body.decode())
            print("Received message:", drone_message_content)

            # 버퍼에 드론 데이터 저장
            message_buffer.insert(0, drone_message_content)
            if len(message_buffer) > BUFFER_SIZE:
                message_buffer.pop()

            # 새로운 드론인지 확인 후 클라이언트에 추가
            drone_id = drone_message_content["drone"]["droneId"]
            if drone_id not in tracked_drones:
                tracked_drones.add(drone_id)
                print(f"New drone detected: {drone_id}")

            # 데이터베이스에 비동기적으로 저장
            await save_to_db(drone_message_content)
            print("DroneMessage saved to MongoDB")

        except Exception as error:
            print("Error processing message:", error)


async def consume_drone_message():
    try:
        connection = await connect_robust("amqp://localhost")
        channel = await connection.channel()
        queue = await channel.declare_queue("Drone_message", durable=False)

        await queue.consume(process_message)
        print("Waiting for messages in Drone_message queue...")

    except Exception as error:
        print("Failed to consume messages:", error)


@app.on_event("startup")
async def startup_event():
    await consume_drone_message()


@app.get("/api/positions")
async def get_positions():
    try:
        # 메모리 버퍼에서 최신 5개 드론 위치 데이터 가져오기
        recent_positions = message_buffer[:5]
        filtered_positions = [
            {
                "droneId": position["drone"]["droneId"],
                "latitude": position["drone"]["latitude"],
                "longitude": position["drone"]["longitude"],
                "name": position["drone"]["name"],
            }
            for position in recent_positions
        ]
        return filtered_positions

    except Exception as error:
        print("Error fetching drone positions:", error)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/drone/{drone_id}")
async def get_drone_details(drone_id: str):
    try:
        # 메모리 버퍼에서 드론 ID로 데이터를 검색
        drone_message = next(
            (msg for msg in message_buffer if msg["drone"]["droneId"] == drone_id), None
        )

        if not drone_message:
            raise HTTPException(status_code=404, detail="Drone not found")

        # ObjectId를 문자열로 변환하여 반환
        return object_id_to_str(drone_message)

    except Exception as error:
        print("Error fetching drone details:", error)
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", 5000)))
