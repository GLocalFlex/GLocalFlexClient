from dataclasses import dataclass
import argparse
from enum import Enum

class Side(Enum):
    BUY = 'buy'
    SELL = 'sell'


@dataclass
class SellerBuyerSettings:
    """
    Dataclass for storing the settings for the buyer and seller.

    quantity will be in the range btween min and max
    price will be in the range btween min and max
    wait multiplier is multiplied with sleep time 
    """
    quantity_min: int 
    quantity_max: int
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
    test: bool = False

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
    parser.add_argument('side', choices=['buy', 'sell'])
    parser.add_argument("-r", "--run", dest="run_time", metavar="", type=int, default=config.params.runtime, help=f"Running time in seconds. 0 runs forever. Default: {config.params.runtime}")
    parser.add_argument("-s", "--sleep", dest="sleep_time", metavar="", type=float, default=config.params.frequency, help=f"Sleep time per cycle. Default: {config.params.frequency}")
    parser.add_argument('--log', dest='log', action='store_true')
    parser.add_argument("--host", default=config.market.host, dest="host", metavar="", help=f"Host url, DEFAULT: {config.market.host}")
    parser.add_argument("--test", dest="test", action="store_true", help=f"Test mode. Does not require you to specify all order params, missing details will be filled with random values.")
    parser.add_argument("-u", dest="username", metavar="", help=f"Username")
    parser.add_argument("-p", dest="password", metavar="", help=f"Password")

    parser.add_argument("--quantity", dest="quantity", metavar="", help=f"Quantity")
    parser.add_argument("--price", dest="price", metavar="", help=f"Price")
    parser.add_argument("--delivery_start", metavar="", help=f"Delivery start")
    parser.add_argument("--delivery_end", metavar="", help=f"Delivery end")
    parser.add_argument("--location_ids", metavar="", help=f"Location ids")
    parser.add_argument("--country_code", metavar="", help=f"Country code")

    return parser.parse_args()    
