# GLocalFlexClient


Run the main.py directly with:

- python main.py buy
- python main.py sell 

or with multithreading:
- python main_threading.py buy
- python main_threading.py sell

Username and password are taken from environment variables GLF_USER1 and GLF_PASSWD1 if side is 'buy', GLF_USER2 and GLF_PASSWD2 if side is 'sell'.

-r = runtime in seconds (e.g. 60 will stop the script after about a minute, setting zero runs forever)

-s = sleep time in seconds (can be less than zero or exactly 0)

--log = sets logging on. If logging is used, "./log" directory is required.

--host = set the host url as cli argument

Example:
- python main_threading.py sell -r 60 -s 0 --log 

Some hardcoded 'constant' parameters can be adjusted at the beginning of main.py. 

You can also use traderbots.sh script. The script will start several clients at once. Uncomment/comment the relevant lines and modify the parameters. 



Log file format:

Time now, message.

Time now, request response time, buy/sell, quantity, price.

2024-03-01 16:32:57,055 Client started with runtime: 20, side: buy

2024-03-01 16:32:57,068 Client started with runtime: 20, side: sell

2024-03-01 16:32:57,962 0:00:00.653358, buy, 74, 1.2683064318683313

2024-03-01 16:32:58,368 0:00:01.066592, buy, 8, 1.405169489956847
