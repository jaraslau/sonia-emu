import socket
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 5001))

def process(data):
    if data["type"] == "button":
        return bytes(f"b {data['id']} {data['state']}\n", "utf-8")
    else:
        x_id, y_id = (0, 1) if data["id"] == "Left" else (2, 3)
        x = bytes(f"j {x_id} {data['x'] * 512}\n", "utf-8")
        y = bytes(f"j {y_id} {data['y'] * 512}\n", "utf-8")
        return (x, y)

@app.route("/input", methods=["POST"])
def handle_input():
    data = request.json
    
    if data["type"] == "button":
        sock.send(process(data))
    elif data["type"] == "joystick":
        [ sock.send(axis) for axis in process(data) ]

    return jsonify({"status": "success", "message": "Data received"})

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0")
    except:
        sock.close()
