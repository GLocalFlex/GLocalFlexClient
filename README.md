# GLocalFlexClient

The repository contains a simple automated Rest client that acts as a seller or buyer and a websocket client listening to live updates.

The rest client is able to automatically create buy and sell orders. The parameters are set in the `rest_client.py` file.

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
    --sim          Simulation mode. Generates random buy or sell orders Order paramaters ranges are specified rest_client.py.
    --quantity     Quantity
    --price        Price
    --delivery_start Delivery start
    --delivery_end Delivery end
    --location_ids Location ids
    --country_code Country code

Example
    
    # seller
    python3 rest_client.py sell --log --host test.glocalflexmarket.com -u username -p password --price 1.0 --quantity 100 --delivery_start 2025-01-29T00:00:00 --delivery_end 2025-01-29309:00:00 --location_id loc1,loc2 --country_code FI

    #  buyer
    python3 rest_client.py buy --log --host test.glocalflexmarket.com -u username -p password -r 60 --sim

The websocket client is able to listen for live events such as ticker, order updates, expired orders and orderbook updates.

    usage: ws_client.py [-h] [--host] [-u] [-p] [-t]

    WebSocket Example Client Listener

    options:
    -h, --help        show this help message and exit
    --host            Host url, DEFAULT: test.glocalflexmarket.com
    --port            Host port, DEFAULT: 443
    -u , --username   Username for authentication, default: <username>
    -p , --password   Password for authentication, default: <password>
    -t , --endpoint   Order API endpoint, default: /api/v1/ws/trade/, endpoints: /api/v1/ws/trade/ /api/v1/ws/ticker/ /api/v1/ws/orderbook/
    -d , --debug      Enable websocket debug mode

Example:

    python3 ws_client.py --host test.glocalflexmarket.com -u username -p password