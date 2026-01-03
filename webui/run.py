#!/usr/bin/env python3
import time
import logging
import sys
import argparse
import uvicorn
from socket import socket, AF_UNIX, SOCK_STREAM
import webui

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s")
logger.setLevel(logging.INFO)

def get_args():
    parser = argparse.ArgumentParser(
        description="SoniaEmu WebUI",
        epilog="This software is licensed under MIT license",
        add_help=False,
    )
    parser.add_argument(
        "-p", "--port", type=int, default=5000, help="port on which webui is hosted"
    )
    parser.add_argument(
        "-h", "--host", type=str, default="0.0.0.0", help="address to host on"
    )
    parser.add_argument(
        "-s",
        "--socket",
        type=str,
        default="/tmp/sonia-emu.sock",
        help="path to a Unix Socket",
    )
    parser.add_argument(
        "-f",
        "--fail",
        action="store_true",
        help="exit on failed connection to a Unix socket",
    )
    parser.add_argument(
        "-r",
        "--reconnect",
        type=int,
        default=5,
        help="waiting time between reconnections (if less than 0, reconnects once)",
    )
    parser.add_argument(
        "--max-tries", type=int, default=5, help="max_tries between reconnections"
    )
    parser.add_argument("--help", action="help", help="show this help message and exit")
    return parser.parse_args()

def connect(sock_path: str, reconnect: int, max_tries: int) -> bool:
    for attempt in range(max_tries):
        try:
            sock = socket(AF_UNIX, SOCK_STREAM)
            sock.connect(sock_path)
            sock.setblocking(False)
            webui.sock = sock
            logger.info(f"Connected to a socket at {sock_path}")
            return True
        except Exception as e:
            sock.close()
            logger.error(f"Connection to {sock_path} failed: {e}")
            if reconnect > 0:
                for i in range(reconnect):
                    print(f"Reconnecting in {reconnect - i}s", end="\r", flush=True)
                    time.sleep(1)
                logger.info(f"Trying to reconnect to {sock_path}")
            else:
                return False
    return False

def main(args):
    if sys.platform != "linux":
        logger.warning(
            f"This program was written specifically for Linux. Input events won't work on {sys.platform}."
        )
    try:
        is_connected = connect(args.socket, args.reconnect, args.max_tries)
        if not is_connected:
            if args.fail:
                logger.error(f"Failed to connect to {args.socket}. Exiting...")
                return
            else:
                logger.warning(f"Failed to connect to {args.socket}. Starting WebUI anyway...")
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        if args.fail:
            if hasattr(webui, "sock") and webui.sock:
                webui.sock.close()
            return
    uvicorn.run("webui:app", port=args.port, host=args.host, loop="uvloop")

if __name__ == "__main__":
    args = get_args()
    main(args)