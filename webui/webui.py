import asyncio
import orjson
import logging
import struct
from socket import socket, AF_UNIX, SOCK_STREAM
from dataclasses import dataclass
from typing import Literal
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(json_loads=orjson.loads)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

sock = socket(AF_UNIX, SOCK_STREAM)
sock.setblocking(False)

logger = logging.getLogger(__name__)

@dataclass
class InputData:
    AXIS_RANGE = 512
    PREFIX_MAP = {"button": b"b", "joystick": b"j", "trigger": b"j"}

    input_type: Literal["button", "joystick", "trigger"]
    input_id: int
    input_value: float

    def to_bytes(self) -> bytes:
        if self.input_type != "button":
            value = int(self.input_value * self.AXIS_RANGE)
        else:
            value = int(self.input_value)
        prefix = self.PREFIX_MAP[self.input_type]
        return struct.pack("!BBi", prefix[0], self.input_id, value)

async def send_data(data: dict, sock: socket) -> None:
    loop = asyncio.get_running_loop()
    try:
        input_data = InputData(data["type"], data["id"], data["value"])
        packet = input_data.to_bytes()
        await loop.sock_sendall(sock, packet)
    except Exception as e:
        logger.error(f"An error occurred: {e}")

@app.post("/fallback")
async def handle_fetch(request: Request):
    data = await request.json()
    await send_data(data, sock)
    return {"status": "ok"}

@app.websocket("/ws")
async def handle_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            data = orjson.loads(raw)
            await send_data(data, sock)
    except WebSocketDisconnect:
        logger.warning("Websocket disconnected, running on fallback")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.on_event("shutdown")
async def shutdown():
    sock.close()