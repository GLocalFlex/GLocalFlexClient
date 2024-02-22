#list of users and their info

# [username, password, side, quantity_min, quantity_max, unit_price_min, unit_price_max, probability_of_order]
# username, password, side: str
# quantity:int
# unit_price: float
# probability: float between 0.0 and 1.0

# Example:
# ['testuser', 'mypassword', 'buy', 50, 100, 0.1, 0.4, 0.2]

# How long the program runs, how much wait between cycles. Small sleeptime & high probabilities result in lots of traffic.
runtime = 10
sleeptime = 0.01
verbose = True

userlist = [
['pelle-test1', 'NAKKImakkara1', 'buy', 1, 100,  0.5, 1.5, 0.2],
['pelle-test2', 'NAKKImakkara2', 'buy', 10, 100, 0.4, 1.5, 0.1],
['pelle-test3', 'NAKKImakkara3', 'sell', 1, 10, 0.5, 1.6, 0.5],
['pelle-test4', 'NAKKImakkara4', 'sell', 1, 10, 0.4, 1.5, 0.4],
['pelle-test5', 'NAKKImakkara5', 'sell', 1, 20, 0.8, 1.5, 0.3]

]


