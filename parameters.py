
"""
Parameters and default values for parameters in the GLocalFlex test client.
"""

import datetime
import os

# How long the program runs and how long wait per cycle.
RUN_TIME = 5
SLEEP_TIME = 0.1

BUYER_USERNAME = os.getenv("GLF_USER1", "<username>")
BUYER_PASSWORD = os.getenv("GLF_PASSWD1", "<password>")

SELLER_USERNAME = os.getenv("GLF_USER2", "<username>")
SELLER_PASSWORD = os.getenv("GLF_PASSWD2", "<password>")

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


# set timezone to UTC
TZ = datetime.timezone.utc
HOST = os.getenv("GFLEX_URL", "test.glocalflexmarket.com")
#HOST = os.getenv("GFLEX_URL", "glocalflexmarket.com")
CLIENT_ID = "glocalflexmarket_public_api"
AUTH_ENDPOINT = "/auth/oauth/v2/token"
ORDER_ENDPOINT = "/api/v1/order/"
SSL_VERIFY = True
