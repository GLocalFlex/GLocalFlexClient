
import time
import os
import argparse
import random
import json
import requests
import datetime as dt
from datetime import datetime
from dataclasses import dataclass

from userdata import userlist
from userdata import runtime
from userdata import sleeptime
from userdata import verbose

# set timezone to UTC
TZ = dt.timezone.utc
HOST = os.getenv("GFLEX_URL", "glocalflexmarket.com")
USERNAME = os.getenv("GFLEX_USER", "<username>")
PASSWORD = os.getenv("GFLEX_PASSWORD", "<password>")
CLIENT_ID = "glocalflexmarket_public_api"
AUTH_ENDPOINT = "/auth/oauth/v2/token"
ORDER_ENDPOINT = "/api/v1/order/"
SSL_VERIFY = True

@dataclass
class Token:
    """Data container to hold access token and refresh token information"""
    access_token: str
    refresh_token: str
    expires_in_sec: int
    grant_time: datetime = None

class FlexCustomer:
    def __init__(self, user, passwd, side='buy', 
                 qmin = 10,     #minimum quantity
                 qmax = 100,    #maximum quantity
                 pmin = 0.1,    #minimum unit price
                 pmax = 0.4,    #maximum unit price
                 prob = 0.5     #probability of trading [0.0-1.0]
                 ) -> None:
        
        self.username = user
        self.password = passwd

        self.side = side
        self.qmin = qmin
        self.qmax = qmax
        self.pmin = pmin
        self.pmax = pmax
        self.prob = prob

        self.auth_url = f"https://{HOST}{AUTH_ENDPOINT}"
        self.order_url = f"https://{HOST}{ORDER_ENDPOINT}"
        self.client_id  = CLIENT_ID
        self.verify = SSL_VERIFY

        #self.token = self.authenticate(user, passwd, self.auth_url)
        #print (self.token)

    def format_time(self, time):
        return time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    
    def request_token(self, client_id: str, username: str, password: str, token_url: str,  ssl_verify: bool =True) -> requests.Response:
        """Request access token with username and password"""

        payload = {
            "client_id": client_id,
            "grant_type": "password",
            "username": username,
            "password": password,
        }

        response = requests.post(
            token_url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            verify=ssl_verify,
        )
        return response

    def check_auth_response(self, response):

        # set the time the token was granted
        time_granted = datetime.now(TZ)

        oauth_resp = response.json()
        # print(json.dumps(oauth_resp, indent=4))
        token = Token(
            oauth_resp["access_token"],
            oauth_resp["refresh_token"],
            oauth_resp["expires_in"],
            time_granted,
        )
        return token
    
    def authenticate(self):
        """Authenticates and returns access token."""
        auth_url = self.auth_url
        client_id = self.client_id
        user = self.username
        secret = self.password
        ssl_verify = self.verify
        # get access token with username and password
        auth_response = self.request_token(token_url=auth_url,
                                    client_id=client_id,
                                    username=user,
                                    password=secret,
                                    ssl_verify=ssl_verify)

        if auth_response.status_code != 200:
            print(f"Failed to get token from response {auth_response.text}")
            print(f"Exiting...")
            return None

        token: Token = self.check_auth_response(auth_response)
        return token
    
    def create_order(self, timezone, side: str, quantity: int, unit_price: float):
        """Create a buy or sell order with random quantity and price for demonstration purposes"""

        time_now = datetime.now(timezone)
        return {
            "side": side,
            "quantity": quantity, 
            "price": unit_price,
            "delivery_start": self.format_time(time_now + dt.timedelta(hours=1)),
            "delivery_end": self.format_time(time_now + dt.timedelta(hours=2)),
            "expiry_time": self.format_time(time_now + dt.timedelta(minutes=10)),
            "order_type": "partialFill",
            "location": {"location_id": ["some_id"],
                        "country_code": "CZ"}, # optional CZ, GE, CH, FI, ES
            "metering": {"metering_id": ["some_id"]}
        }

    def submit_order(self, endpoint: str, access_token: Token, order: dict, ssl_verify: bool =True) -> requests.Response:
        """make a post request with access token to marketplace"""

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        response = requests.post(endpoint, headers=headers, verify=ssl_verify, json=order)

        return response

    def make_order(self):
        #print (self.username, self.token)

        rndval= random.random()
        #print (rndval, self.prob)
        if self.prob > rndval:
            quantity = random.randint(self.qmin, self.qmax)
            price = random.uniform(self.pmin, self.pmax)
            #print (self.username, self.side, quantity, price)

            #Authenticate at the server and get access token
            self.token = self.authenticate()
            #print (self.username, self.token)

            order = self.create_order(TZ, self.side, quantity, price)
            response = self.submit_order(endpoint=self.order_url,
                              access_token=self.token.access_token,
                              order=order,
                              ssl_verify=self.verify)
            #print (response)
            return (self.username, rndval, self.side, quantity, price, response)
        else:
            return (self.username, rndval)


def run():
    # initialize a list of traders
    traders = []
    for user in userlist:
        traders.append(FlexCustomer(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7]))
        # user[username, password, side, quantity_min, quantity_max, unit_price_min, unit_price_max, probability_of_order]

    # Loop through the user for a given time. Each time a trader has a change to submit a buy or sell order.
    starttime = time.time() 
    while time.time() < starttime + runtime:
        for trader in traders:
            tradeStatus = trader.make_order()
            if verbose == True:
                print (tradeStatus)
            time.sleep(sleeptime)


if __name__ == "__main__":
    run()