import asyncio
import orjson
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

@dataclass
class InputData:
    AXIS_RANGE = 512
    PREFIX_MAP = {"button": "b", "joystick": "j", "trigger": "j"}

    input_type: Literal["button", "joystick", "trigger"]
    input_id: int
    input_value: float

    def format(self) -> bytes:
        if self.input_type != "button":
            value = float(self.input_value) * self.AXIS_RANGE
        else:
            value = float(self.input_value)
        prefix = self.PREFIX_MAP[self.input_type]
        return b"%b %d %d\n" % (prefix.encode("ascii"), int(self.input_id), value)

async def send_data(data: dict, sock: socket) -> None:
    loop = asyncio.get_running_loop()
    try:
        input_data = InputData(data["type"], data["id"], data["value"])
        cmd = input_data.format()
        await loop.sock_sendall(sock, cmd)
    except WebSocketDisconnect:
        print("Websocket disconnected, running on fallback")
    except Exception as e:
        print(f"An error occurred: {e}")

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
    except Exception as e:
        print(f"An error occurred: {e}")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.on_event("shutdown")
async def shutdown():
    sock.close()