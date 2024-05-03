
"""
Parameters and default values for parameters in the GLocalFlex test client.
"""

# How long the program runs and how long wait per cycle.
RUN_TIME = 5
SLEEP_TIME = 0.1

# limits for randomized quantity, price and sleeptime multiplier
BUYER_VALUES ={
    'quantity_min' : 100, 
    'quantity_max' : 10000  ,
    'unit_price_min' : 0.1,
    'unit_price_max' : 1,
    'wait_multiplier_min' : 1, 
    'wait_multiplier_max' : 10,
    }
SELLER_VALUES ={
    'quantity_min' : 100, 
    'quantity_max' : 10000,
    'unit_price_min' : 0.1,
    'unit_price_max' : 1,
    'wait_multiplier_min' : 1, 
    'wait_multiplier_max' : 10,
    }


