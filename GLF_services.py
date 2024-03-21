
import requests
import datetime as dt

class Authenticate:
    """Authentication methods for getting new access token and refreshing it with a refresh token."""
    def __init__(self,
                username: str,
                password : str,
                client_id: str, 
                host: str, 
                auth_endpoint: str,  
                timezone, 
                verify = True
                ) -> None:
        """Initialize user with login data"""
        self.client_id = client_id
        self.timezone = timezone
        self.verify = verify

        self.auth_url = f"https://{host}{auth_endpoint}"   

        #make payload for new access token request
        self.new_token_payload = {
                        "client_id": self.client_id,
                        "grant_type": "password",
                        "username": username,
                        "password": password,
                        }

    def token_new(self) -> None:
        """Request a new access token. """
        self.time_granted = dt.datetime.now(self.timezone)
        response = requests.post(
                            self.auth_url,
                            data=self.new_token_payload, 
                            headers={"Content-Type": "application/x-www-form-urlencoded"},
                            verify=self.verify
                            )
        if response.status_code == 200: #200 means succesfull
            token_data = response.json()
            self.access_token  = token_data["access_token"]
            self.refresh_token = token_data["refresh_token"]
            self.token_expires_in = token_data["expires_in"]
        else:
            raise Exception(f"Failed to get token: {response.text}")
        
    def token_refresh(self) -> None:
        """Refresh the access token. """
        #make payload for refreshing the access token
        refresh_token_payload = {
                "client_id": self.client_id,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                }
        
        self.time_granted = dt.datetime.now(self.timezone)
        response = requests.post(
                self.auth_url, 
                data=refresh_token_payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                verify=self.verify
                )

        if response.status_code == 200:
            token_data = response.json()
            self.access_token  = token_data["access_token"]
            self.refresh_token = token_data["refresh_token"]
            self.token_expires_in = token_data["expires_in"]
        else:
            raise Exception(f"Failed to refresh token: {response.text}")

    def token_check_expiry(self) -> bool:
        """Check if the token is about to expire in 5 seconds """
        token_still_valid = True
        if self.time_granted + dt.timedelta(seconds = (self.token_expires_in - 5)) < dt.datetime.now(self.timezone):
            token_still_valid  = False
        return token_still_valid


class Order:
    def format_order(self, side: str, quantity: int, unit_price: float) -> dict:
        """Format the order data to be suitable for the server."""
        
        def format_time(time):
            return time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        time_now = dt.datetime.now(self.timezone)

        #round times to next fifteen minutes 
        if time_now.minute <15:
            time_now.replace(minute=15, second=0, microsecond=0)
        elif time_now.minute < 30:
            time_now.replace(minute=30, second=0, microsecond=0)
        elif time_now.minute < 45:
            time_now.replace(minute=45, second=0, microsecond=0)
        else:
            time_now.replace(hour=time_now.hour +1, minute=0, second=0, microsecond=0)

        return {
            "side": side,
            "quantity": quantity, 
            "price": unit_price,
            "delivery_start": format_time(time_now + dt.timedelta(hours=1)),
            "delivery_end": format_time(time_now + dt.timedelta(hours=2)),
            "expiry_time": format_time(time_now + dt.timedelta(minutes=10)),
            "order_type": "partialFill",
            "location": {"location_id": ["some_id"],
                        "country_code": "CZ"}, # optional CZ, GE, CH, FI, ES
            "metering": {"metering_id": ["some_id"]}
        }

    def submit_order(self, order: dict) -> requests.Response:
        """Send post request to marketplace."""

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        response = requests.post(self.order_url, headers=headers, verify=self.verify, json=order)
        return response

    def make_order(self, side: str, quantity: int, unit_price: float) -> requests.Response:
        """Make an order, side= 'buy' or 'sell'."""
        order = self.format_order(side, quantity, unit_price)
        response = self.submit_order(order)
        return response


class GLF_Client(Authenticate, Order):
    """GLocalFlex client that inherits the methods for authentication an submitting orders."""
    def __init__(self, username: str, password: str, client_id: str, host: str, auth_endpoint: str, order_endpoint : str, timezone, verify=True) -> None:
        super().__init__(username, password, client_id, host, auth_endpoint, timezone, verify)

        #Define order_url here, all other necessary stuff is defined by Authenticate.
        self.order_url = f"https://{host}{order_endpoint}" 


