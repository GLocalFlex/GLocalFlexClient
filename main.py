
import time
import random
import argparse
import logging
import datetime
import os

from client import Client
import parameters as par #parameters in a separate file for easy modification


# set timezone to UTC
TZ = datetime.timezone.utc
HOST = os.getenv("GFLEX_URL", "dev.glocalflexmarket.com")
#HOST = os.getenv("GFLEX_URL", "glocalflexmarket.com")
CLIENT_ID = "glocalflexmarket_public_api"
AUTH_ENDPOINT = "/auth/oauth/v2/token"
ORDER_ENDPOINT = "/api/v1/order/"
SSL_VERIFY = True

def cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create buy or sell orders")
    parser.add_argument('side', choices=['buy', 'sell'])
    parser.add_argument("-r", "--run", dest="run_time", metavar="", type=int, default=par.RUN_TIME, help=f"Running time in seconds.")
    parser.add_argument("-s", "--sleep", dest="sleep_time", metavar="", type=int, default=par.SLEEP_TIME, help=f"Sleep time per cycle.")
    parser.add_argument('--log', dest='log', action='store_true')
    parser.add_argument("--host", default=HOST, dest="host", metavar="", help=f"Host url, DEFAULT: {HOST}")
    parser.add_argument("-u", dest="username", metavar="", help=f"Username")
    parser.add_argument("-p", dest="password", metavar="", help=f"Password")
    return parser.parse_args()

def log_response(code: int, text: str, quantity: int, price: float) -> None:
    if code == 200:
        logging.info(f'{code}, {side}, {quantity}, {price}')  
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
    
    if side == 'buy':
        qmin = par.BUYER_VALUES["quantity_min"]
        qmax = par.BUYER_VALUES["quantity_max"]

        pmin = par.BUYER_VALUES["unit_price_min"]
        pmax = par.BUYER_VALUES["unit_price_max"]

        wmin = par.BUYER_VALUES["wait_multiplier_min"]
        wmax = par.BUYER_VALUES["wait_multiplier_max"]
        location_ids = random.choice([[None], ["loc1", "loc2", "loc3"], ["loc.*"]])


    if side == 'sell':
        qmin = par.SELLER_VALUES["quantity_min"]
        qmax = par.SELLER_VALUES["quantity_max"]

        pmin = par.SELLER_VALUES["unit_price_min"]
        pmax = par.SELLER_VALUES["unit_price_max"]

        wmin = par.SELLER_VALUES["wait_multiplier_min"]
        wmax = par.SELLER_VALUES["wait_multiplier_max"]
        location_ids = random.choice([["loc1", "loc2", "loc3"], ['loc1']])


    user = Client(username, password, client_id, host, auth_endpoint, order_endpoint, timezone, verify=verify)
    user.token_new()

    starttime = time.time() 
    while True:
        if run_time != 0: #setting to 0 runs forever
            if time.time() > starttime + run_time:
                break

        if user.token_check_expiry():
            user.token_refresh()

        """Makes the order and logs result."""
        try:
            quantity = random.randrange(qmin, qmax, 100)
            price = round(random.uniform(pmin, pmax), 2)    
            order_status = user.make_order(side, quantity, price, location_ids)

            log_response(order_status.status_code, order_status.text, quantity, price)
                    
        except Exception as e:
            logging.error(repr(e))


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