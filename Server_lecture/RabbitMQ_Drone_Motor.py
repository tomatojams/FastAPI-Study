## 패키지 설치시 P.Tmind 미들웨어가 깨지기때문에 다른 환경에서

import os
import json
from fastapi import FastAPI, HTTPException
from mongoengine import (
    connect,
    Document,
    StringField,
    FloatField,
    BooleanField,
    IntField,
    DictField,
)
from aio_pika import connect_robust, IncomingMessage
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# MongoDB 연결 설정
mongo_url = os.getenv("MONGODB_LOCAL_URL")
connect(host=mongo_url)

# 메시지를 버퍼로 임시 저장할 메모리 기반의 큐
BUFFER_SIZE = 30
message_buffer = []

# 클라이언트 요청을 위한 드론 목록
tracked_drones = set()


class Drone(Document):
    name = StringField()
    frequency = FloatField()
    bandwidth = FloatField()
    allow_track = BooleanField()
    allow_takeover = BooleanField()
    class_name = StringField()
    radio_resources = IntField()
    droneId = StringField(required=True, unique=True)
    latitude = FloatField()
    longitude = FloatField()

    meta = {"collection": "drone"}  # MongoDB 컬렉션 이름을 명시적으로 지정


class DroneMessage(Document):
    message = StringField(
        choices=["FOUND", "WARNING", "ERROR", "VERIFY", "TEST"], required=True
    )
    sender_id = StringField(required=True)
    drone = DictField()  # Drone 정보를 포함하는 필드

    meta = {"collection": "server_message"}  # MongoDB 컬렉션 이름을 명시적으로 지정


async def save_to_db(drone_message_content: dict):
    try:
        drone_message = DroneMessage(**drone_message_content)
        drone_message.save()
        return str(drone_message.id)
    except Exception as e:
        print(f"Error saving to MongoDB: {e}")
        raise


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

            # 데이터베이스에 저장
            await save_to_db(drone_message_content)
            print("DroneMessage saved to MongoDB")

        except Exception as error:
            print("Error processing message:", error)


async def consume_drone_message():
    try:
        # RabbitMQ에 연결
        connection = await connect_robust("amqp://localhost/")
        channel = await connection.channel()

        # 큐 선언 및 소비 시작
        queue = await channel.declare_queue("Drone_message", durable=False)
        await queue.consume(process_message)

        print("Waiting for messages in Drone_message queue...")

    except Exception as error:
        print(f"Failed to consume messages: {error}")


@app.on_event("startup")
async def startup_event():
    # 애플리케이션 시작 시 RabbitMQ 연결 및 메시지 소비 시작
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

        return drone_message

    except Exception as error:
        print("Error fetching drone details:", error)
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", 5000)))
