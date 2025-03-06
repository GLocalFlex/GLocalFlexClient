# GLocalFlexClient

The repository contains a simple automated Rest client that acts as a seller or buyer and a websocket client listening to live updates.

The rest client is able to automatically create buy and sell orders. The parameters are set in the `rest_client.py` file.

    usage: rest_client.py [-h] [--host] [-u] [-p] [-r] [-s] [--log] [--run-once] [--power] [--price] [--delivery-start]
                        [--delivery-end] [--expiry-time] [--location-ids] [--country-code]
                        {buy,sell}

    Create buy or sell orders

    positional arguments:
    {buy,sell}

    options:
    -h, --help         show this help message and exit
    --host             Host url, DEFAULT: test.glocalflexmarket.com
    -u                 Username
    -p                 Password
    -r , --run         Running time in seconds. 0 runs forever, -1 sends one order and exits, same as --run-once option.
                        Default: 0
    -s , --sleep       Time between order requests. Default: 1
    --log              Log orders output to file
    --run-once         Send order once and exit
    --power            Power in Watt
    --price            Price in €/kWh
    --delivery-start   Delivery start UTC time format 2025-01-29T00:00:00, Default: current time + 1h
    --delivery-end     Delivery end UTC time format 2025-01-29T00:00:00, Default: current time + 2h
    --expiry-time      Expiry time UTC time format 2025-01-29T00:00:00, , Default: current time + 10min
    --location-ids     Location ids
    --country-code     Country code, options ['CZ', 'DE', 'CH', 'ES', 'FI', 'FR', '']


Minimal Example

    # sends one buy order
    python3 rest_client/rest_client.py buy --host test.glocalflexmarket.com -u your_username -p your_password --run-once


    # sends one sell order
    python3 rest_client/rest_client.py sell --host test.glocalflexmarket.com -u your_username -p your_password --run-once

Example
    
    # seller
    python3 rest_client.py sell --log --host test.glocalflexmarket.com -u your_username -p your_password --price 1.0 --power 100 --delivery_start '2025-01-31T14:45:00.000Z' --delivery_end '2025-01-31T15:45:00.000Z' --location_id loc1,loc2 --country_code FI

    #  buyer
    python3 rest_client.py buy --log --host test.glocalflexmarket.com -u your_username -p your_password -r 60

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

    # receives the latest trades
    python3 ws_client.py --host test.glocalflexmarket.com -u your_username -p your_password -t /api/v1/ws/ticker
    # receives the latest orderbook
    python3 ws_client.py --host test.glocalflexmarket.com -u your_username -p your_password -t /api/v1/ws/orderbook/
    # receives the latest updates of your order
    python3 ws_client.py --host test.glocalflexmarket.com -u your_username -p your_password -t /api/v1/ws/trade/ 

