
import requests
import datetime as dt
import logging

class Auth:
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

        self.access_token  = None
        self.refresh_token = None
        self.token_expires_in = None

        #make payload for new access token request
        self.new_token_payload = {
                        "client_id": self.client_id,
                        "grant_type": "password",
                        "username": username,
                        "password": password,
                        }

    def token_new(self) -> bool:
        """Request a new access token. """
        logging.info("Authenticate user, request new access token")
        self.time_granted = dt.datetime.now(self.timezone)
        response = requests.post(
                            self.auth_url,
                            data=self.new_token_payload, 
                            headers={"Content-Type": "application/x-www-form-urlencoded"},
                            verify=self.verify
                            )
        if response.status_code == 200:
            token_data = response.json()
            self.access_token  = token_data["access_token"]
            self.refresh_token = token_data["refresh_token"]
            self.token_expires_in = token_data["expires_in"]
            logging.info("Authentication success")
            return True
        else:
            logging.error(f"Request failed with code: {response.status_code}")
            logging.error(f"Failed to refresh token: {response.reason}")
            return False
        
    def token_refresh(self) -> bool:
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
            return True
        else:
           logging.error(f"Request failed with code: {response.status_code}")
           logging.error(f"Failed to refresh token: {response.reason}")
           return False

    def token_check_expiry(self) -> bool:
        """Check if the token is about to expire. """
        if self.token_expires_in is None:
            return True
        _time_bedore_expiry= 60
        token_expires_soon = False
        if self.time_granted + dt.timedelta(seconds = (self.token_expires_in - _time_bedore_expiry)) < dt.datetime.now(self.timezone):
            token_expires_soon  = True
        return token_expires_soon




