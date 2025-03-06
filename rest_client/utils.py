from dataclasses import dataclass
import argparse
from enum import Enum

import const

class Side(Enum):
    BUY = 'buy'
    SELL = 'sell'


@dataclass
class SellerBuyerSettings:
    """
    Dataclass for storing the settings for the buyer and seller.

    power will be in the range btween min and max
    price will be in the range btween min and max
    wait multiplier is multiplied with sleep time 
    """
    power_min: int 
    power_max: int
    unit_price_min: float
    unit_price_max: float
    wait_multiplier_min: int
    wait_multiplier_max: int
    baseline: dict = None


@dataclass
class UserConfig:
    username: str = None
    password: str = None

@dataclass
class EndpointConfig:
    auth: str
    order: str

@dataclass
class Parameters:
    side: str
    runtime: float
    timezone: str
    frequency: float = -1
    log: bool = False
    run_only_once: bool = False

@dataclass
class HostConfig:
    host: str
    client_id: str
    ssl_verify: bool
    api: EndpointConfig

@dataclass
class DefaultConfig:
    market: HostConfig
    user: UserConfig
    params: Parameters
    buyer: SellerBuyerSettings = None
    seller: SellerBuyerSettings = None

def cli_args(config: DefaultConfig) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create buy or sell orders")
    parser.add_argument("--host", default=config.market.host, dest="host", metavar="", help=f"Host url, DEFAULT: {config.market.host}")
    parser.add_argument("-u", dest="username", metavar="", help=f"Username")
    parser.add_argument("-p", dest="password", metavar="", help=f"Password")
    parser.add_argument('side', choices=['buy', 'sell'])
    parser.add_argument("-r", "--run", dest="run_time", metavar="", type=int, default=config.params.runtime, help=f"Running time in seconds. 0 runs forever, -1 sends one order and exits, same as --run-once option. Default: {config.params.runtime}")
    parser.add_argument("-s", "--sleep", dest="sleep_time", metavar="", type=float, default=config.params.frequency, help=f"Time between order requests. Default: {config.params.frequency}")
    parser.add_argument('--log', dest='log', action='store_true', help=f"Log orders output to file")
    parser.add_argument("--run-once", dest="once", action="store_true", help=f"Send order once and exit")

    # order option to override default settings
    parser.add_argument("--power", dest="power", metavar="", help=f"Power in Watt")
    parser.add_argument("--price", dest="price", metavar="", help=f"Price in €/kWh")
    parser.add_argument("--delivery-start", metavar="", default=None, help=f"Delivery start UTC time format 2025-01-29T00:00:00, Default: current time + 1h")
    parser.add_argument("--delivery-end", metavar="", default=None, help=f"Delivery end  UTC time format 2025-01-29T00:00:00, Default: current time + 2h")
    parser.add_argument("--expiry-time", metavar="", default=None, help=f"Expiry time UTC time format 2025-01-29T00:00:00, , Default: current time + 10min")
    parser.add_argument("--location-ids", metavar="", default=None, help=f"Location ids")
    parser.add_argument("--country-code", metavar="", default=None, help=f"Country code, options {const.COUNTRY_CODES_ALLOWED}")

    return parser.parse_args()    
