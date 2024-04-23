
import time
import random
import argparse
import logging
import threading

from GLF_services import GLF_Client
import parameters as par #parameters in a separate file for easy modification

def run(side: str, run_time: int, sleep_time: int, host: str, multithreading_enable: bool):
    if side == 'buy':
        username = par.BUYER_USERNAME
        password = par.BUYER_PASSWORD
        qmin = par.BUYER_VALUES["quantity_min"]
        qmax = par.BUYER_VALUES["quantity_max"]

        pmin = par.BUYER_VALUES["unit_price_min"]
        pmax = par.BUYER_VALUES["unit_price_max"]

        wmin = par.BUYER_VALUES["wait_multiplier_min"]
        wmax = par.BUYER_VALUES["wait_multiplier_max"]

    if side == 'sell':
        username = par.SELLER_USERNAME
        password = par.SELLER_PASSWORD
        qmin = par.SELLER_VALUES["quantity_min"]
        qmax = par.SELLER_VALUES["quantity_max"]

        pmin = par.SELLER_VALUES["unit_price_min"]
        pmax = par.SELLER_VALUES["unit_price_max"]

        wmin = par.SELLER_VALUES["wait_multiplier_min"]
        wmax = par.SELLER_VALUES["wait_multiplier_max"]

    # username = USERNAME1
    # password = PASSWORD1
    client_id = par.CLIENT_ID
    #host = HOST  # now as cli
    auth_endpoint = par.AUTH_ENDPOINT
    order_endpoint = par.ORDER_ENDPOINT
    timezone = par.TZ
    verify = par.SSL_VERIFY

    user = GLF_Client(username, password, client_id, host, auth_endpoint, order_endpoint, timezone, verify=True)
    user.token_new()

    starttime = time.time() 
    while True:
        if run_time != 0: #setting to 0 runs forever
            if time.time() > starttime + run_time:
                break

        if user.token_check_expiry():
            #token about to expire
            user.token_refresh()

        def func_order():
            """Makes the order and logs result."""
            try:
                quantity = random.randint(qmin, qmax)
                price = random.uniform(pmin, pmax)    
                order_status = user.make_order(side, quantity, price)
                
                if order_status.status_code == 200:
                    logging.info(f'{order_status.elapsed}, {side}, {quantity}, {price}')  
                elif order_status.status_code == 401:
                    user.token_new()
                    logging.debug(f'Debug: 401 Get new token.')
                elif order_status.status_code == 429:
                    logging.warning(f'Warning: 429 Too many requests.')
                elif order_status.status_code == 422:
                    logging.error(f'Error: 422 Unprocessable Content: {order_status.text}.')
                else:
                    logging.error(f'Error: Unexpected code: {order_status.text}')

            except Exception as e:
                logging.error(repr(e))

        if multithreading_enable == True:
            t = threading.Thread(target=func_order)
            t.start()
        else:
            func_order()

        sleep_multiplier  = random.randint(wmin, wmax)
        time.sleep(sleep_time*sleep_multiplier)
    
    logging.info(f'Finished, side: {side}')


def cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create buy or sell orders")
    parser.add_argument('side', choices=['buy', 'sell'])
    parser.add_argument("-r", "--run", dest="run_time", metavar="", type=int, default=par.RUN_TIME, help=f"Running time in seconds.")
    parser.add_argument("-s", "--sleep", dest="sleep_time", metavar="", type=int, default=par.SLEEP_TIME, help=f"Sleep time per cycle.")
    parser.add_argument("--host", default=par.HOST, dest="host", metavar="", help=f"Host url, DEFAULT: {par.HOST}")
    parser.add_argument('--mt', dest='mt_enable', action='store_true', help=f"Run with multithreading.")
    parser.add_argument('--log', dest='log', action='store_true')
    return parser.parse_args()

if __name__ == "__main__":
    args = cli_args()
    side = args.side
    run_time = args.run_time
    log = args.log
    host = args.host
    multithreading_enable  = args.mt_enable
    sleep_time = args.sleep_time

    if log == True:
        logging.basicConfig(filename='./gflex_client.log', encoding='utf-8', level=logging.INFO, format='%(asctime)s %(message)s')
        logging.info(f'Client started with run time: {run_time}, side: {side}, multithreading: {multithreading_enable}')

    #side = 'buy'
    run(side, run_time, sleep_time, host, multithreading_enable)
