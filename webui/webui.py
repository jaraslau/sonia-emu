import os
import orjson
import logging
import struct
from contextlib import asynccontextmanager
from typing import Literal, ClassVar, AsyncGenerator, cast
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from utils.socket import Socket

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    app.state.sock = Socket(os.getenv("SOCK_PATH", "/tmp/sonia-emu.sock"))
    await app.state.sock.connect()
    if app.state.sock.writer is None:
        logger.warning("Starting WebUI anyway...")
    try:
        yield
    finally:
        if app.state.sock is not None:
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


class InputData(BaseModel):
    AXIS_RANGE: ClassVar[int] = 512
    PREFIX_MAP: ClassVar[dict[str, bytes]] = {
        "button": b"b",
        "joystick": b"j",
        "trigger": b"j",
    }

    type: Literal["button", "joystick", "trigger"]
    id: int
    value: float

    def to_bytes(self) -> bytes:
        if self.type != "button":
            val = int(self.value * self.AXIS_RANGE)
        else:
            val = int(self.value)
        prefix = self.PREFIX_MAP[self.type]
        return struct.pack("!BBi", prefix[0], self.id, val)


async def get_sock(request: Request) -> Socket:
    return cast(Socket, request.app.state.sock)


async def send_data(input_data: InputData, sock: Socket) -> None:
    try:
        packet = input_data.to_bytes()
        await sock.sendall(packet)
    except Exception as e:
        logger.error(e)


@app.post("/fallback")
async def handle_fetch(
    input_data: InputData, sock: Socket = Depends(get_sock)
) -> dict[str, str]:
    await send_data(input_data, sock)
    return {"status": "ok"}


@app.websocket("/ws")
async def handle_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    sock: Socket = websocket.app.state.sock
    try:
        while True:
            raw = await websocket.receive_text()
            data = orjson.loads(raw)
            input_data = InputData(**data)
            await send_data(input_data, sock)
    except WebSocketDisconnect:
        logger.warning("Websocket disconnected, running on fallback")
    except Exception as e:
        logger.error(e)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="index.html")
