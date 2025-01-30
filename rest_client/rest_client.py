
from curses.ascii import SI
import time
import random
import argparse
import logging
import datetime as dt
import os
import ssl
from dataclasses import dataclass
import urllib3
import requests
from auth import Auth

from utils import SellerBuyerSettings, cli_args, DefaultConfig, HostConfig, UserConfig, EndpointConfig, Parameters
from utils import Side
import warnings
warnings.filterwarnings("ignore", message="Unverified HTTPS request")


HOST = os.getenv("GFLEX_URL", "test.glocalflexmarket.com")
CLIENT_ID = "glocalflexmarket_public_api"
AUTH_ENDPOINT = "/auth/oauth/v2/token"
ORDER_ENDPOINT = "/api/v1/order/"
SSL_VERIFY = False
DEFAULT_SLEEP_TIME = 1 # sleep time between cycles
DEFAULT_RUN_TIME = 0 # run time in seconds, 0 runs forever
COUNTRY_CODES_ALLOWED = ["CZ", "DE", "CH", "ES", "FI", "FR", ""]

HTTP_AUTHENTICATION_ERROR = 401

baseline_data = {
            "metering_id": "ce15bc33-2bda-4d26-8ddd-b958b22b569b",
            "created_at": "2019-08-24T14:15:00Z",
            "reading_start": "2019-08-24T14:15:00Z",
            "reading_end": "2019-08-24T14:30:00Z",
            "resolution": 1,
            "direction": "consumption",
            "quality": "estimated",
            "energy_product": "apparent",
            "unit_measured": "kWh",
            "data_points": [{"2019-08-24T14:15:00Z": 1}]
    }



config = DefaultConfig(
    market=HostConfig(
        host=HOST,
        client_id=CLIENT_ID,
        ssl_verify=SSL_VERIFY,
        api=EndpointConfig(
            auth=AUTH_ENDPOINT,
            order=ORDER_ENDPOINT
        ),
    ),
    user=UserConfig(
        username=None,
        password=None,
    ),
    params=Parameters(
        runtime=DEFAULT_RUN_TIME,
        frequency=DEFAULT_SLEEP_TIME,
        timezone=dt.timezone.utc,
        side=Side.BUY,
    ),
    buyer=SellerBuyerSettings(
        quantity_min=1000,
        quantity_max=2000,
        unit_price_min=0.5,
        unit_price_max=1.5,
        wait_multiplier_min=1,
        wait_multiplier_max=5,
    ),
    seller=SellerBuyerSettings(
        quantity_min=100,
        quantity_max=10000,
        unit_price_min=0.1,
        unit_price_max=1,
        wait_multiplier_min=1,
        wait_multiplier_max=5,
        baseline=baseline_data,
    ),
)


@dataclass
class Order:
    side: str
    location_ids: list[str] = None
    country_code: str = None
    quantity: float = None
    price: float = None
    delivery_start: dt.datetime = None
    delivery_end: dt.datetime = None
    expiry_time: dt.datetime = None
    baseline: dict = None

    def as_dict(self) -> dict:
        d = self.__dict__
        if self.side == Side.BUY:
            # remove baseline key from buy order
            d.pop("baseline")
        
        return {
            "side": self.side,
            "power": float(self.quantity),
            "price": float(self.price),
            "delivery_start": self.delivery_start,
            "delivery_end": self.delivery_end,
            "expiry_time": self.expiry_time,
            "location": {"location_id": self.location_ids,
                        "country_code": self.country_code}
        }


class Client:
    """GLocalFlex REST client"""

    def __init__(self, config: DefaultConfig, cli_order: Order) -> None:

        self.config = config
        self.order = cli_order
        #Define order_url here, all other necessary stuff is defined by Authenticate.
        self.order_url = f"https://{config.market.host}{config.market.api.order}" 
        self.verify = config.market.ssl_verify
        self.auth: Auth = Auth(config.user.username,
                               config.user.password,
                               config.market.client_id,
                               config.market.host,
                               config.market.api.auth,
                               config.params.timezone,
                               config.market.ssl_verify) 

    def send_order(self, order: dict) -> requests.Response:
        """Send post request to marketplace."""

        headers = {
            "Authorization": f"Bearer {self.auth.access_token}",
            "Content-Type": "application/json",
        }
        response = requests.post(self.order_url, headers=headers, verify=self.verify, json=order)
        return response


    def set_order_parameters(self, values: SellerBuyerSettings, side: str, order: Order) -> tuple[Order, int, int]:
            def format_time(time):
                return time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

            def round_quarter(t: dt.datetime) -> dt.datetime:
                """Round the time to the nearest quarter hour 00, 15, 30, 45"""
                minute = t.minute
                if minute % 15 != 0:
                    t += dt.timedelta(minutes=15 - (minute % 15))
                return t.replace(second=0, microsecond=0)
            
            wmin = values.wait_multiplier_min
            wmax = values.wait_multiplier_max                


            if order.quantity is not None:
                quantity = order.quantity
            else:
                quantity = random.randrange(values.quantity_min, values.quantity_max, 100)
            
            if order.price is not None:
                price = order.price
            else:  
                price = round(random.uniform(values.unit_price_min, values.unit_price_max), 2)
            
            if order.country_code is not None:
                country_code = order.country_code
            else:
                country_code = random.choice(COUNTRY_CODES_ALLOWED)

            if order.location_ids is not None:
                location_ids = order.location_ids
            else:
                location_ids = [None]

            time_now = dt.datetime.now(self.config.params.timezone)
                
            if order.delivery_start is not None:
                delivery_start = dt.datetime.fromisoformat(order.delivery_start)
            else:
                delivery_start = round_quarter(time_now + dt.timedelta(hours=1))
            
            if order.delivery_end is not None:
                delivery_end = dt.datetime.fromisoformat(order.delivery_end)
            else:
                delivery_end = round_quarter(time_now + dt.timedelta(hours=2))




            return Order(side="buy" if side == Side.BUY else "sell",
                        location_ids=location_ids,
                        country_code=country_code,
                        quantity=quantity,
                        price=price,
                        delivery_start= format_time(delivery_start),
                        delivery_end=format_time(delivery_end),
                        expiry_time=format_time(time_now + dt.timedelta(minutes=10)),

                        baseline=baseline_data if side == Side.SELL else None
                        ), wmin, wmax
        
    @staticmethod
    def log_response(code: int, text: str, params: Order) -> None:
        if code == 200:
            logging.info(f'status={code}, side={params.side}, power={params.quantity}, '
                        f'price={params.price}, country={params.country_code}, loc_ids={params.location_ids}')  
        elif code == 401:
            logging.debug(f'Debug: 401 Get new token.')
        elif code == 429:
            logging.warning(f'Warning: 429 Too many requests.')
        elif code == 422:
            logging.error(f'Error: 422 Unprocessable Content: {text}.')
        else:
            logging.error(f'Request failed with code {code}')

        


    def run(self):
        

        logging.info(f"Target url {self.config.market.host}")
        self.auth.token_new()

        starttime = time.time() 
        while True:
            
            if self.config.params.runtime > 0: #setting to 0 runs forever
                if time.time() > starttime + self.config.params.runtime:
                    break

            if self.auth.token_check_expiry():
                if not self.auth.token_refresh():
                    while not self.auth.token_new():
                        time.sleep(5)

            if self.config.params.side == Side.BUY:
                order, wmin, wmax = self.set_order_parameters(config.buyer, Side.BUY, self.order)
            if self.config.params.side == Side.SELL:
                order, wmin, wmax = self.set_order_parameters(config.seller, Side.SELL, self.order)
              
            try:
                response = self.send_order(order.as_dict())
            except (ssl.SSLError) as e:
                logging.error(f'Error: {e}')
                time.sleep(5)
                continue
            except (urllib3.exceptions.NewConnectionError, requests.exceptions.ConnectionError) as e:
                logging.error(f'Marketplace is not available')
                logging.error(f'Error: {e}')
                time.sleep(5)
                continue

            if response.status_code == HTTP_AUTHENTICATION_ERROR:
                while not self.auth.token_new():
                    time.sleep(5)

            self.log_response(response.status_code, response.text, order)

            if config.params.runtime == -1:
                break

            sleep_multiplier  = random.randint(wmin, wmax)
            time.sleep(self.config.params.frequency*sleep_multiplier)
        
        logging.info(f'Finished, side: {order.side}')


def main():
    args = cli_args(config)
    config.market.host = args.host
    config.user.username = args.username
    config.user.password = args.password
    config.params.runtime = args.run_time
    config.params.frequency = args.sleep_time
    config.params.log = args.log
    config.params.side = Side(args.side)
    config.params.test = args.test

    new_order = Order(
        side= args.side,
        quantity= args.quantity,
        price= args.price,
        delivery_start= args.delivery_start,
        delivery_end= args.delivery_end,
        location_ids= args.location_ids.split(",") if args.location_ids is not None else None,
        country_code= args.country_code,
    )


    
    client = Client(config, new_order)

    if config.params.log == True:
        logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s %(message)s')
        logging.info(f'Client started with runtime: {config.params.runtime}, side: {config.params.side}')
        if config.params.test == True:
            logging.info(f'Test mode enabled')

        if config.params.test == False and  new_order.quantity is None:
            logging.warning(f'No quantity set!')
            return
        if config.params.test == False and new_order.price is None:
            logging.warning(f'No price set!')
            return
        if config.params.test == False and new_order.delivery_start is None:
            logging.warning(f'No delivery start set!')
            return
        if config.params.test == False and new_order.delivery_end is None:
            logging.warning(f'No delivery end set!')
            return
        if config.params.test == False and new_order.country_code is None:
            logging.warning(f'No country code set!')
            return

    try:
        client.run()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
