
import time
import random
import json
import logging
import datetime as dt
import os
import ssl
import warnings
from dataclasses import dataclass
import urllib3
import requests
from auth import Auth

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

import const

from utils import SellerBuyerSettings, cli_args, DefaultConfig, HostConfig, UserConfig, EndpointConfig, Parameters
from utils import Side

logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s  %(module)s %(lineno)d: %(message)s')

HOST = os.getenv("GFLEX_URL", "test.glocalflexmarket.com")


# Baseline data example used in sell orders

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

# Buyer and seller Settings for simulation mode
buyer_params = SellerBuyerSettings(
        power_min=1000, # range flexibility power
        power_max=2000,
        unit_price_min=0.5, # range unit price Eur/kWh
        unit_price_max=1.5,
        wait_multiplier_min=1, # randomises wait time between order requests
        wait_multiplier_max=5,
    )

seller_params = SellerBuyerSettings(
        power_min=100,
        power_max=10000,
        unit_price_min=0.1, 
        unit_price_max=1,
        wait_multiplier_min=1,
        wait_multiplier_max=5,
        baseline=baseline_data,
    )


config = DefaultConfig(
    market=HostConfig(
        host=HOST,
        client_id=const.CLIENT_ID,
        ssl_verify=const.SSL_VERIFY,
        api=EndpointConfig(
            auth=const.AUTH_ENDPOINT,
            order=const.ORDER_ENDPOINT
        ),
    ),
    user=UserConfig(
        username=None,
        password=None,
    ),
    params=Parameters(
        runtime=const.DEFAULT_RUN_TIME,
        frequency=const.DEFAULT_SLEEP_TIME,
        timezone=dt.timezone.utc,
        side=Side.BUY,
    ),
    buyer=buyer_params,
    seller=seller_params,
)


@dataclass
class Order:
    side: str
    location_ids: list[str] = None
    country_code: str = None
    power: float = None
    price: float = None
    delivery_start: dt.datetime = None
    delivery_end: dt.datetime = None
    expiry_time: dt.datetime = None
    baseline: dict = None

    def as_dict(self) -> dict:
        return {
            "side": self.side,
            "power": float(self.power),
            "price": float(self.price),
            "delivery_start": self.delivery_start,
            "delivery_end": self.delivery_end,
            "expiry_time": self.expiry_time,
            "location": {"location_id": self.location_ids,
                        "country_code": self.country_code},
            "baseline": self.baseline
        }


class Client:
    """GLocalFlex REST client"""

    def __init__(self, config: DefaultConfig, cli_order: Order) -> None:

        self.config = config
        self.cli_order_params = cli_order
        self.run_once = config.params.run_only_once

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


    def set_random_order_parameters(self, values: SellerBuyerSettings, side: str, config: DefaultConfig) -> tuple[Order, int, int]:
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

            time_now = dt.datetime.now(config.params.timezone)
            power = random.randrange(values.power_min, values.power_max, 100)
            price =round(random.uniform(values.unit_price_min, values.unit_price_max), 2)
            country_code = random.choice(const.COUNTRY_CODES_ALLOWED)
            location_ids = [None]
            delivery_start = round_quarter(time_now + dt.timedelta(hours=1)) 
            delivery_end = round_quarter(time_now + dt.timedelta(hours=2))
            expiry_time=format_time(time_now + dt.timedelta(minutes=10))

            random_order = Order(side="buy" if side == Side.BUY else "sell",
                        location_ids=location_ids,
                        country_code=country_code,
                        power=power,
                        price=price,
                        delivery_start= format_time(delivery_start),
                        delivery_end=format_time(delivery_end),
                        expiry_time=expiry_time,
                        baseline=baseline_data if side == Side.SELL else None
                        )
            
            order = self._overide_order_client_args(self.cli_order_params, random_order)
            return order, wmin, wmax

    def _overide_order_client_args(self, cli_args: Order, order: Order) -> Order:
        order.power = cli_args.power if cli_args.power is not None else order.power
        order.price = cli_args.price if cli_args.price is not None else order.price
        order.delivery_start = cli_args.delivery_start  if cli_args.delivery_start is not None else order.delivery_start
        order.delivery_end = cli_args.delivery_end if cli_args.delivery_end  is not None else order.delivery_end
        order.expiry_time = cli_args.expiry_time if cli_args.expiry_time is not None else order.expiry_time
        order.country_code = cli_args.country_code if cli_args.country_code is not None else order.country_code
        order.location_ids = cli_args.location_ids if cli_args.location_ids is not None else order.location_ids
        return order
        

            
    @staticmethod
    def log_response(code: int, text: str, params: Order) -> None:
        if code == 200:
            logging.info(f'http request status code={code}, side={params.side}, power={params.power}, '
                        f'price={params.price}, country={params.country_code}, loc_ids={params.location_ids}')  
        elif code == 401:
            logging.debug(f'Debug: 401 Get new token.')
        elif code == 429:
            logging.warning(f'Warning: 429 Too many requests.')
        elif code == 422:
            logging.error(f'Error: 422 Unprocessable Content: {text}.')
        else:
            logging.error(f'Request failed with code {code}')
            logging.error(f'Response: {text}')

        


    def run(self):
        
        # set up file logger
        if self.config.params.log:
            logging.FileHandler('client_orders.log')
            


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
                order, wmin, wmax = self.set_random_order_parameters(config.buyer, Side.BUY, self.config)
            if self.config.params.side == Side.SELL:
                order, wmin, wmax = self.set_random_order_parameters(config.seller, Side.SELL, self.config)
              
            logging.info(f'Sending order: {json.dumps(order.as_dict(), indent=4)}') 
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

            if response.status_code == const.HTTP_AUTHENTICATION_ERROR:
                while not self.auth.token_new():
                    time.sleep(5)

            self.log_response(response.status_code, response.text, order)

            if config.params.runtime == -1 or self.run_once:
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
    config.params.run_only_once = args.once

    cli_args_order = Order(
        side= args.side,
        power= args.power,
        price= args.price,
        delivery_start= args.delivery_start,
        delivery_end= args.delivery_end,
        expiry_time= args.expiry_time,
        location_ids= args.location_ids.split(",") if args.location_ids is not None else None,
        country_code= args.country_code,
    )

    client = Client(config, cli_args_order)

    logging.info(f'Client started with runtime: {config.params.runtime}, side: {config.params.side}')

    try:
        client.run()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
