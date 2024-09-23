
import time
import random
import argparse
import logging
import datetime
import os

from client import Client

import warnings
warnings.filterwarnings("ignore", message="Unverified HTTPS request")


TZ = datetime.timezone.utc
HOST = os.getenv("GFLEX_URL", "test.glocalflexmarket.com")
CLIENT_ID = "glocalflexmarket_public_api"
AUTH_ENDPOINT = "/auth/oauth/v2/token"
ORDER_ENDPOINT = "/api/v1/order/"
SSL_VERIFY = True

"""
Parameters and default values for parameters in the GLocalFlex test client.
"""

SLEEP_TIME = 1 # sleep time between cycles
RUN_TIME = 0 # run time in seconds, 0 runs forever

# limits for randomized quantity, price and sleeptime multiplier
BUYER_VALUES ={
    'quantity_min' : 5000,  # order quantity will be in the range btween min and max
    'quantity_max' : 50000  ,
    'unit_price_min' : 0.5, # order price will be in the range btween min and max
    'unit_price_max' : 1.5,
    'wait_multiplier_min' : 1, # is multiplied with sleep time 
    'wait_multiplier_max' : 5,
    }

SELLER_VALUES ={
    'quantity_min' : 100, 
    'quantity_max' : 10000,
    'unit_price_min' : 0.1,
    'unit_price_max' : 1,
    'wait_multiplier_min' : 1, 
    'wait_multiplier_max' : 5,
    }


def cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create buy or sell orders")
    parser.add_argument('side', choices=['buy', 'sell'])
    parser.add_argument("-r", "--run", dest="run_time", metavar="", type=int, default=RUN_TIME, help=f"Running time in seconds. 0 runs forever. Default: {RUN_TIME}")
    parser.add_argument("-s", "--sleep", dest="sleep_time", metavar="", type=float, default=SLEEP_TIME, help=f"Sleep time per cycle. Default: {SLEEP_TIME}")
    parser.add_argument('--log', dest='log', action='store_true')
    parser.add_argument("--host", default=HOST, dest="host", metavar="", help=f"Host url, DEFAULT: {HOST}")
    parser.add_argument("-u", dest="username", metavar="", help=f"Username")
    parser.add_argument("-p", dest="password", metavar="", help=f"Password")
    return parser.parse_args()

def log_response(code: int, text: str, quantity: int, price: float, country: str) -> None:
    if code == 200:
        logging.info(f'status={code}, side={side}, power={quantity}, price={price}, country={country}')  
    elif code == 401:
        user.token_new()
        logging.debug(f'Debug: 401 Get new token.')
    elif code == 429:
        logging.warning(f'Warning: 429 Too many requests.')
    elif code == 422:
        logging.error(f'Error: 422 Unprocessable Content: {text}.')
    else:
        logging.error(f'Error: Unexpected code: {text}')

def run(side: str, run_time: int, sleep_time: int, args: argparse.Namespace):
    
    client_id = CLIENT_ID
    auth_endpoint = AUTH_ENDPOINT
    order_endpoint = ORDER_ENDPOINT
    timezone = TZ
    verify = SSL_VERIFY

    host = args.host
    username = args.username
    password = args.password
    


    logging.info(f"Target url {host}")
    user = Client(username, password, client_id, host, auth_endpoint, order_endpoint, timezone, verify=verify)
    user.token_new()

    starttime = time.time() 
    while True:
        country_code = random.choice(["CZ", "DE", "CH", "ES", "FI", "FR", ""]) # optional CZ, DE, CH, FI, ES
        
        if side == 'buy':
            qmin = BUYER_VALUES["quantity_min"]
            qmax = BUYER_VALUES["quantity_max"]

            pmin = BUYER_VALUES["unit_price_min"]
            pmax = BUYER_VALUES["unit_price_max"]

            wmin = BUYER_VALUES["wait_multiplier_min"]
            wmax = BUYER_VALUES["wait_multiplier_max"]
            location_ids = random.choice([[None], ["loc1", "loc2", "loc3"], ["loc.*"]])


        if side == 'sell':
            qmin = SELLER_VALUES["quantity_min"]
            qmax = SELLER_VALUES["quantity_max"]

            pmin = SELLER_VALUES["unit_price_min"]
            pmax = SELLER_VALUES["unit_price_max"]

            wmin = SELLER_VALUES["wait_multiplier_min"]
            wmax = SELLER_VALUES["wait_multiplier_max"]
            location_ids = random.choice([["loc1", "loc2", "loc3"], ['loc1']])        

        if run_time != 0: #setting to 0 runs forever
            if time.time() > starttime + run_time:
                break

        if user.token_check_expiry():
            success = user.token_refresh()
            if not success:
                user.token_new()

        """Makes the order and logs result."""
        # try:
        quantity = random.randrange(qmin, qmax, 100)
        price = round(random.uniform(pmin, pmax), 2)    
        order_status = user.make_order(side, quantity, price, location_ids, country_code)

        log_response(order_status.status_code, order_status.text, quantity, price, country_code)
                
        # except Exception as e:
        #     logging.error(repr(e))


        sleep_multiplier  = random.randint(wmin, wmax)
        time.sleep(sleep_time*sleep_multiplier)
    
    logging.info(f'Finished, side: {side}')


if __name__ == "__main__":
    args = cli_args()
    side = args.side
    run_time = args.run_time
    log = args.log
    sleep_time = args.sleep_time

    if log == True:
        logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s %(message)s')
        logging.info(f'Client started with runtime: {run_time}, side: {side}')

    try:
        run(side, run_time, sleep_time, args)
    except KeyboardInterrupt:
        pass
