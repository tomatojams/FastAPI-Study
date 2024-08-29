

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from langchain_core.callbacks import StreamingStdOutCallbackHandler

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import json
from typing import List
from langchain_openai import ChatOpenAI
# 아래 것들이 아닌 위의걸 써야함
# from langchain_community.llms import OpenAI
# from langchain.llms import OpenAI
import getpass
import os

from starlette.middleware.cors import CORSMiddleware

load_dotenv('.env')

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{input}")
])


os.environ["OPENAI_API_KEY"] = getpass.getpass()

llm = ChatOpenAI(model_name="gpt-3.5-turbo",streaming = True, callbacks=[StreamingStdOutCallbackHandler()], temperature=1, max_tokens=500)
# llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

output_parser = StrOutputParser()
# Chain
chain = prompt | llm.with_config({"run_name": "model"}) | output_parser.with_config({"run_name": "Assistant"})


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)["message"]
            try:
                # Stream the response
                async for chunk in chain.astream_events({'input': message}, version="v1", include_names=["Assistant"]):
                    if chunk["event"] in ["on_parser_start", "on_parser_stream"]:
                        await manager.send_personal_message(json.dumps(chunk), websocket)
            except Exception as e:
                print(e)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/chat/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)["message"]
            try:
                # Stream the response
                async for chunk in chain.astream_events({'input': message}, version="v1", include_names=["Assistant"]):
                    if chunk["event"] in ["on_parser_start", "on_parser_stream"]:
                        await manager.send_personal_message(json.dumps(chunk), websocket)
            except Exception as e:
                print(e)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)