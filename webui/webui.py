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
axis_range = 512

def process_axes(data: dict) -> bytes | tuple[bytes, bytes]:
    x_id, y_id = (0, 1) if data["id"] == "Left" else (2, 3)
    x = bytes(f"j {x_id} {data['x'] * axis_range}\n", "utf-8")
    y = bytes(f"j {y_id} {data['y'] * axis_range}\n", "utf-8")
    return (x, y)

async def send_data(data: dict, sock) -> None:
    loop = asyncio.get_running_loop()
    if data["type"] == "button":
        processed = bytes(f"b {data['id']} {data['state']}\n", "utf-8")
        await loop.sock_sendall(sock, processed)
    elif data["type"] == "trigger":
        processed = bytes(f"j {data['id']} {data['z'] * axis_range}\n", "utf-8")
        await loop.sock_sendall(sock, processed)
    elif data["type"] == "joystick":
        tasks = [loop.sock_sendall(sock, axis) for axis in process_axes(data)]
        await asyncio.gather(*tasks)

@app.post("/fallback")
async def handle_fetch(request: Request):
    data = await request.json()
    await send_data(data, sock)
    return {"status": "success", "message": "Data received"}

@app.websocket("/ws")
async def handle_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            await send_data(data, sock)
    except Exception as e:
        print(f"An error occured: {e}")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
