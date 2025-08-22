import socket
import asyncio
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.setblocking(False)

AXIS_RANGE = 512
BUTTON_TEMPLATE = "b {} {}\n"
TRIGGER_TEMPLATE = "j {} {}\n"
AXIS_MAP = {"Left": (0, 1), "Right": (2, 3)}

def process_axes(data):
    x_id, y_id = AXIS_MAP[data["id"]]
    x_val = int(data["x"] * AXIS_RANGE)
    y_val = int(data["y"] * AXIS_RANGE)
    return (
        f"j {x_id} {x_val}\n".encode(),
        f"j {y_id} {y_val}\n".encode())

async def send_data(data, sock):
    loop = asyncio.get_running_loop()
    try:
        if data["type"] == "button":
            cmd = BUTTON_TEMPLATE.format(data["id"], data["state"]).encode()
            await loop.sock_sendall(sock, cmd)
        elif data["type"] == "trigger":
            cmd = TRIGGER_TEMPLATE.format(data["id"], int(data["z"] * AXIS_RANGE)).encode()
            await loop.sock_sendall(sock, cmd)
        elif data["type"] == "joystick":
            x_cmd, y_cmd = process_axes(data)
            await loop.sock_sendall(sock, x_cmd + y_cmd)
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
