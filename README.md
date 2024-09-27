# GLocalFlexClient

The reposistory contains simple automated Rest client that acts as seller or buyer and a websocket client listening to live updates. 

The rest client is able to automaticallty create buy and sell orders. The paramaters are set in the `rest_client.py` file.


    usage: rest_client.py [-h] [-r] [-s] [--log] [--host] [-u] [-p] {buy,sell}

    Create buy or sell orders

    positional arguments:
    {buy,sell}

    options:
    -h, --help     show this help message and exit
    -r , --run     Running time in seconds. 0 runs forever. Default: 0
    -s , --sleep   Sleep time per cycle. Default: 1
    --log
    --host         Host url, DEFAULT: test.glocalflexmarket.com
    -u             Username
    -p             Password


Example
    
    # seller
    python rest_client.py sell --log --host test.glocalflexmarket.com -u username -p password -r 60

    #  buyer
    python rest_client.py buy --log --host test.glocalflexmarket.com -u username -p password -r 60 

The websocket client is able to listen for live events such as ticker, order updates, expired orders and orderbook updates.

    usage: ws_client.py [-h] [--host] [-u] [-p] [-t]

    WebSocket Example Client Listener

    options:
    -h, --help        show this help message and exit
    --host            Host url, DEFAULT: test.glocalflexmarket.com
    -u , --username   Username for authentication, default: <username>
    -p , --password   Password for authentication, default: <password>
    -t , --endpoint   Order API endpoint, default: /api/v1/ws/trade/, endpoints: /api/v1/ws/trade/ /api/v1/ws/ticker/ /api/v1/ws/orderbook/

Example:

    python3 ws_client.py --host test.glocalflexmarket.com -u username -p password 

