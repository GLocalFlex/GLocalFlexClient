
import datetime as dt
import os
import time
import random
import argparse

from GLF_services import GLF_client


#** Almost constant values**
# set timezone to UTC
TZ = dt.timezone.utc
HOST = os.getenv("GFLEX_URL", "glocalflexmarket.com")
CLIENT_ID = "glocalflexmarket_public_api"
AUTH_ENDPOINT = "/auth/oauth/v2/token"
ORDER_ENDPOINT = "/api/v1/order/"
SSL_VERIFY = True

# **These need to find their place **
#how long the script runs and how fast
runtime = 5
sleeptime = 0.001


# limits for randomized quantity, price and sleeptime multiplier
BUYER_VALUES ={
    'quantity_min' : 1, 
    'quantity_max' : 100,
    'unit_price_min' : 0.8,
    'unit_price_max' : 1.8,
    'wait_multiplier_min' : 10, 
    'wait_multiplier_max' : 100,
    }
SELLER_VALUES ={
    'quantity_min' : 1, 
    'quantity_max' : 10,
    'unit_price_min' : 1.0,
    'unit_price_max' : 2.0,
    'wait_multiplier_min' : 1, 
    'wait_multiplier_max' : 10,
    }


def run(side):

    if side == 'buy':
        username = os.getenv("GLF_USER1", "<username>")
        password = os.getenv("GLF_PASSWD1", "<password>")
        qmin = BUYER_VALUES["quantity_min"]
        qmax = BUYER_VALUES["quantity_max"]

        pmin = BUYER_VALUES["unit_price_min"]
        pmax = BUYER_VALUES["unit_price_max"]

        wmin = BUYER_VALUES["wait_multiplier_min"]
        wmax = BUYER_VALUES["wait_multiplier_max"]

    if side == 'sell':
        username = os.getenv("GLF_USER2", "<username>")
        password = os.getenv("GLF_PASSWD2", "<password>")
        qmin = SELLER_VALUES["quantity_min"]
        qmax = SELLER_VALUES["quantity_max"]

        pmin = SELLER_VALUES["unit_price_min"]
        pmax = SELLER_VALUES["unit_price_max"]

        wmin = SELLER_VALUES["wait_multiplier_min"]
        wmax = SELLER_VALUES["wait_multiplier_max"]

    # username = USERNAME1
    # password = PASSWORD1
    client_id = CLIENT_ID
    host = HOST
    auth_endpoint = AUTH_ENDPOINT
    order_endpoint = ORDER_ENDPOINT
    timezone = TZ
    verify = SSL_VERIFY

    user = GLF_client(username, password, client_id, host, auth_endpoint, order_endpoint, timezone, verify=True)
    user.token_new()

    starttime = time.time() 
    while time.time() < starttime + runtime:

        quantity = random.randint(qmin, qmax)
        price = random.uniform(pmin, pmax)
        sleep_multiplier  = random.randint(wmin, wmax)

        if not user.token_check_expiry():
            #token about to expire
            user.token_refresh()

        order_status = user.make_order(side, quantity, price)
        #print (order_status.elapsed, side, quantity, price)
        
        if order_status.status_code != 200:
            user.token_new()
    
        time.sleep(sleeptime*sleep_multiplier)


def cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create buy or sell orders")
    parser.add_argument('side', choices=['buy', 'sell'])
    return parser.parse_args()

if __name__ == "__main__":
    args = cli_args()
    side = args.side
    #side = 'buy'
    run(side)
