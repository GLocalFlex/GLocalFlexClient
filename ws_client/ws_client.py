"""
usage: ws_api_listener.py [-h] [--host] [-u] [-p] [-t]

WebSocket Example Client Listener

options:
  -h, --help        show this help message and exit
  --host            Host url, DEFAULT: glocalflexmarket.com
  -u , --username   Username for authentication, default: <username>
  -p , --password   Password for authentication, default: <password>
  -t , --endpoint   Order API endpoint, default: /api/v1/ws/trade
  
Python version: >= 3.10

Dependencies:

pip install websocket-client requests

"""

import argparse
import json
import multiprocessing
import os
import ssl
import threading
from dataclasses import dataclass
from time import sleep

import requests
import websocket

HOST = os.getenv("GFLEX_URL", "test.glocalflexmarket.com")
USERNAME = os.getenv("GFLEX_USER", "<username>")
PASSWORD = os.getenv("GFLEX_PASSWORD", "<password>")

CLIENT_ID = "glocalflexmarket_public_api"
AUTH_ENDPOINT = "/auth/oauth/v2/token"
ORDER_ENDPOINT = "/api/v1/ws/trade/"
AVAILALBLE_ENDPOINT = "/api/v1/ws/trade/ /api/v1/ws/ticker/ /api/v1/ws/orderbook/"
SSL_VERIFY = True
PORT = 443
USER_MESSAGE = "Listen for messages, press Ctrl + c to quit): \n"

class WebSocketClient:
    def __init__(self, url, ssl_enabled=True, token=None):
        self.ws_url = url
        self.ssl_enabled = ssl_enabled
        self.token = token
        self.received_messages = []
        self.shutdown_pipe, self.shutdown_pipe2 = multiprocessing.Pipe()

        if self.token:
            headers = {
                "Authorization": f"Bearer {self.token}",
            }

        self.sslopt = (
            {
                "cert_reqs": ssl.CERT_NONE,
                "check_hostname": False,
                "ssl_context": ssl._create_unverified_context(),
            }
            if ssl_enabled
            else None
        )

        self.ws = websocket.WebSocketApp(
            url=self.ws_url,
            header=headers,
            on_message=self.on_message,
            on_ping=self.on_ping,
            on_close=self.on_close,
        )

        self.receive_thread = threading.Thread(target=self.receive_message, daemon=True)
        self.receive_thread.start()

    def receive_message(self):
        err = self.ws.run_forever(ping_interval=1, sslopt=self.sslopt)
        if err:
            # send exit message to shutdown the mmain thread
            self.shutdown_pipe.send("exit")
            print(f"WebSocket connection error: {err}\n")

    def on_close(self, ws):
        print("WebSocket closed by server")
        self.shutdown_pipe.send("exit")

    def on_message(self, ws, message):
        parsed_message = json.loads(message)
        print(f"Received message:\n {json.dumps(parsed_message, indent=4)} \n")
        print(USER_MESSAGE)
        self.received_messages.append(parsed_message)

    def on_ping(self, ws, data):
        ws.pong()

    def send_message(self, message):
        self.ws.send(message)

    def run(self):
        try:
            print(USER_MESSAGE)
            while True:
                # Check if shutdown signal is received from receive_message thread
                if self.shutdown_pipe2.poll():
                    if self.shutdown_pipe2.recv() == "exit":
                        print("Exiting...")
                        break
                sleep(0.1)

        except KeyboardInterrupt:
            pass
        print("Closing connection...")
        self.ws.close()


@dataclass
class Token:
    access_token: str
    refresh_token: str
    expires_in: int


def request_token(
    client_id: str,
    username: str,
    password: str,
    token_url: str,
    ssl_verify: bool = True,
) -> Token | None:

    payload = {
        "client_id": client_id,
        "grant_type": "password",
        "username": username,
        "password": password,
    }
    response = request_access_token(token_url, payload, ssl_verify=ssl_verify)
    return check_response(response)


def request_access_token(
    token_url: str, payload: dict, ssl_verify=True
) -> requests.Response:
    response = requests.post(
        token_url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        verify=ssl_verify,
    )
    return response


def check_response(response):

    if response.status_code != 200:
        print(f"Failed to get token from response {response}")
        return None

    oauth_resp = response.json()
    token = Token(
        oauth_resp["access_token"],
        oauth_resp["refresh_token"],
        oauth_resp["expires_in"],
    )
    return token


def cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WebSocket Example Client Listener")
    parser.add_argument("--host", default=HOST, dest="host", metavar="", help=f"Host url, DEFAULT: {HOST}")
    parser.add_argument("-u", "--username", dest="username", metavar="", default=USERNAME, help=f"Username for authentication, default: {USERNAME}")
    parser.add_argument("-p", "--password", dest="password", metavar="", default=PASSWORD, help=f"Password for authentication, default: {PASSWORD}")
    parser.add_argument("-t", "--endpoint", dest="endpoint", default=ORDER_ENDPOINT, metavar="", help=f"Order API endpoint, default: {ORDER_ENDPOINT}, endpoints: {AVAILALBLE_ENDPOINT}")
    return parser.parse_args()

def main():

    args = cli_args()
    host = args.host
    user = args.username
    secret = args.password
    ws_endpoint = args.endpoint

    auth_url = f"https://{host}:{PORT}{AUTH_ENDPOINT}"
    ws_url = f"wss://{host}:{PORT}{ws_endpoint}"

    token = request_token(CLIENT_ID, user, secret, auth_url, ssl_verify=SSL_VERIFY)

    if token is None:
        print("Failed to get token")
        return
    # token is used for authencation with the websocket endpoint
    access_token = token.access_token

    print("#############################################################")
    print(f"Connecting to Websocket endpoint {ws_url}")
    print("#############################################################")

    ws_client = WebSocketClient(ws_url, token=access_token)
    ws_client.run()


if __name__ == "__main__":
    main()
