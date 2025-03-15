import socket
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
try:
    sock.connect("/tmp/sonia-emu.sock")
except Exception as e:
    print(f"Connection failed: {e}")
    sock.close()

def process(data):
    if data["type"] == "button":
        return bytes(f"b {data['id']} {data['state']}\n", "utf-8")
    else:
        x_id, y_id = (0, 1) if data["id"] == "Left" else (2, 3)
        x = bytes(f"j {x_id} {data['x'] * 512}\n", "utf-8")
        y = bytes(f"j {y_id} {data['y'] * 512}\n", "utf-8")
        return (x, y)

def send_data(data):
    if data["type"] == "button":
        sock.send(process(data))
    elif data["type"] == "joystick":
        [ sock.send(axis) for axis in process(data) ]

@app.post("/fallback")
async def handle_fetch(request: Request):
    data = await request.json()
    send_data(data)

    return {"status": "success", "message": "Data received"}

@app.websocket("/ws")
async def handle_websocket(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        send_data(data)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
