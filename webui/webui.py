import socket
import asyncio
from dataclasses import dataclass
from typing import Literal
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.setblocking(False)

@dataclass
class InputData():
    INPUT_TEMPLATE = "{} {} {}\n"
    AXIS_RANGE = 512
    PREFIX_MAP = {"button": "b", "joystick": "j", "trigger": "j"}

    input_type: Literal["button", "joystick", "trigger"]
    input_id: int
    input_value: float

    def format(self) -> bytes:
        if self.input_type != "button":
            value = self.input_value * self.AXIS_RANGE
        else:
            value = self.input_value
        prefix = self.PREFIX_MAP[self.input_type]
        return self.INPUT_TEMPLATE.format(prefix, self.input_id, value).encode("ascii")

async def send_data(data, sock):
    loop = asyncio.get_running_loop()
    try:
        input_data = InputData(data["type"], data["id"], data["value"])
        cmd = input_data.format()
        await loop.sock_sendall(sock, cmd)
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
            data = await websocket.receive_json()
            await send_data(data, sock)
    except Exception as e:
        print(f"An error occurred: {e}")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.on_event("shutdown")
async def shutdown():
    sock.close()
