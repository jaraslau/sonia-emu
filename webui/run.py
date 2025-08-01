#!/usr/bin/env python3
import argparse
import uvicorn
from webui import sock

def get_args():
    parser = argparse.ArgumentParser(description="SoniaEmu WebUI", epilog="This software is licensed under MIT license", add_help=False)
    parser.add_argument("-p", "--port", type=int, default=5000, help="port on which webui is hosted")
    parser.add_argument("-h", "--host", type=str, default="0.0.0.0", help="address to host on")
    parser.add_argument("-s", "--socket", type=str, default="/tmp/sonia-emu.sock", help="path to a Unix Socket")
    parser.add_argument("--help", action="help", help="show this help message and exit")
    return parser.parse_args()

def main(args):
    try:
        sock.connect(args.socket)
        print(f"Connected to a socket at {args.socket}")
    except Exception as e:
        print(f"Connection failed: {e}")
        sock.close()
    uvicorn.run("webui:app", port=args.port, host=args.host)

if __name__ == "__main__":
    args = get_args()
    main(args)
