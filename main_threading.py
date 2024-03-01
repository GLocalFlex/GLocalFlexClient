#Version that uses threads

import datetime as dt
import os
import time
import random
import argparse
import logging
import threading

from GLF_services import GLF_client


#default values for how long the script runs and how fast
SLEEP_TIME = 0.1
RUN_TIME = 5

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

#** Almost constant values**
# set timezone to UTC
TZ = dt.timezone.utc
HOST = os.getenv("GFLEX_URL", "test.glocalflexmarket.com")
#HOST = os.getenv("GFLEX_URL", "glocalflexmarket.com")
CLIENT_ID = "glocalflexmarket_public_api"
AUTH_ENDPOINT = "/auth/oauth/v2/token"
ORDER_ENDPOINT = "/api/v1/order/"
SSL_VERIFY = True


def run(side, run_time, sleep_time, host):
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
    #host = HOST  # now as cli
    auth_endpoint = AUTH_ENDPOINT
    order_endpoint = ORDER_ENDPOINT
    timezone = TZ
    verify = SSL_VERIFY

    user = GLF_client(username, password, client_id, host, auth_endpoint, order_endpoint, timezone, verify=True)
    user.token_new()

    starttime = time.time() 
    while True:
        if run_time != 0: #setting to 0 runs forever
            if time.time() > starttime + run_time:
                logging.info('Run time is over.')
                break

        sleep_multiplier  = random.randint(wmin, wmax)

        if not user.token_check_expiry():
            #token about to expire
            user.token_refresh()

        def func_order():
            try:
                quantity = random.randint(qmin, qmax)
                price = random.uniform(pmin, pmax)    
                order_status = user.make_order(side, quantity, price)
                logging.info(f'{order_status.elapsed}, {side}, {quantity}, {price}')            

                if order_status.status_code == 429:
                    logging.warning(f'Warning: 429 Too many requests')
                elif order_status.status_code != 200:
                    user.token_new()
            except Exception as e:
                logging.error(f'ERROR')
                logging.error(repr(e))

        t = threading.Thread(target=func_order)
        t.start()

        # order_status = user.make_order(side, quantity, price)
        # logging.info(f'{order_status.elapsed}, {side}, {quantity}, {price}')
        

        time.sleep(sleep_time*sleep_multiplier)
    
    
    logging.info(f'Finished, side: {side}')


def cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create buy or sell orders")
    parser.add_argument('side', choices=['buy', 'sell'])
    parser.add_argument("-r", "--run", dest="run_time", metavar="", type=int, default=RUN_TIME, help=f"Running time in seconds.")
    parser.add_argument("-s", "--sleep", dest="sleep_time", metavar="", type=int, default=SLEEP_TIME, help=f"Sleep time per cycle.")
    parser.add_argument('--log', dest='log', action='store_true')
    parser.add_argument("--host", default=HOST, dest="host", metavar="", help=f"Host url, DEFAULT: {HOST}")
    return parser.parse_args()

if __name__ == "__main__":
    args = cli_args()
    side = args.side
    run_time = args.run_time
    log = args.log
    host = args.host
    sleep_time = args.sleep_time

    if log == True:
        #log much #!!!dir .log/ needs to exist
        logging.basicConfig(filename='./log/gflex_client.log', encoding='utf-8', level=logging.INFO, format='%(asctime)s %(message)s')
        logging.info(f'Client started with runtime: {run_time}, side: {side}')
    # else:
    #     #log only little, default
    #     logging.basicConfig(filename='./log/gflex_client.log', encoding='utf-8', level=logging.CRITICAL, format='%(asctime)s %(message)s')

    #side = 'buy'
    run(side, run_time, sleep_time, host)
    logging.info ('ALL DONE.')
    
