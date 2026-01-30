import os
import orjson
import logging
import struct
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Literal
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from utils.socket import Socket

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.sock = Socket(os.getenv("SOCK_PATH"))
    await app.state.sock.connect()
    if not app.state.sock:
        logger.warning("Running WebUI anyway...")
    yield
    if app.state.sock:
        await app.state.sock.close()


app = FastAPI(
    lifespan=lifespan,
    json_loads=orjson.loads,
    default_response_class=ORJSONResponse,
    debug=False,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


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


async def get_sock(request: Request) -> Socket:
    return request.app.state.sock


async def send_data(data: dict, sock: Socket) -> None:
    try:
        input_data = InputData(data["type"], int(data["id"]), data["value"])
        packet = input_data.to_bytes()
        await sock.sendall(packet)
    except Exception as e:
        logger.error(e)


@app.post("/fallback")
async def handle_fetch(request: Request, sock: Socket = Depends(get_sock)):
    data = await request.json()
    await send_data(data, sock)
    return {"status": "ok"}


@app.websocket("/ws")
async def handle_websocket(websocket: WebSocket):
    await websocket.accept()
    sock: Socket = websocket.app.state.sock
    try:
        while True:
            raw = await websocket.receive_text()
            data = orjson.loads(raw)
            await send_data(data, sock)
    except WebSocketDisconnect:
        logger.warning("Websocket disconnected, running on fallback")
    except Exception as e:
        logger.error(e)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
