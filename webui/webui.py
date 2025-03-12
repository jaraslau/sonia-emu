import socket
import sys
import json
from flask_sock import Sock
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
ws = Sock(app)

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

def process(data):
    if data["type"] == "button":
        return bytes(f"b {data['id']} {data['state']}\n", "utf-8")
    else:
        x_id, y_id = (0, 1) if data["id"] == "Left" else (2, 3)
        x = bytes(f"j {x_id} {data['x'] * 512}\n", "utf-8")
        y = bytes(f"j {y_id} {data['y'] * 512}\n", "utf-8")
        return (x, y)

@ws.route("/input")
def handle_input(ws):
    while True:
        response = ws.receive()
        data = json.loads(response)
        if data["type"] == "button":
            sock.send(process(data))
        elif data["type"] == "joystick":
            [ sock.send(axis) for axis in process(data) ]

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    try:
        sock.connect("/tmp/sonia-emu.sock")
    except Exception as e:
        print(f"Connection failed: {e}")
        sock.close()
    else:
        try:
            app.run(host="0.0.0.0")
        except:
            sock.close()
        finally:
            sock.close()
else:
    try:
        sock.connect("/tmp/sonia-emu.sock")
    except Exception as e:
        print(f"Connection failed: {e}")
        sock.close()

