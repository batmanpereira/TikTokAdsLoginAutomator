"""AdsPower API integration for browser profile management."""
import requests
import logging
import time
from config import (
    ADSPOWER_API_URL, ADSPOWER_CREATE_PROFILE,
    ADSPOWER_OPEN_URL, ADSPOWER_CLOSE_URL,
    ADSPOWER_TIMEOUT, MAX_RETRIES, RETRY_DELAY
)

class AdsPowerAPI:
    def __init__(self):
        self.base_url = ADSPOWER_API_URL

    def _make_request(self, method, endpoint, **kwargs):
        """Make HTTP request to AdsPower API with retries."""
        kwargs.setdefault('timeout', ADSPOWER_TIMEOUT)
        
        for attempt in range(MAX_RETRIES):
            try:
                if method.lower() == 'get':
                    response = requests.get(f"{self.base_url}{endpoint}", **kwargs)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", **kwargs)
                
                if response.status_code == 200:
                    return response.json()
                    
            except requests.exceptions.RequestException as e:
                logging.error(f"AdsPower API request failed (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
                
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
        
        raise Exception("Failed to connect to AdsPower API after multiple retries")

    def check_connection(self):
        """Check if AdsPower is running and accessible."""
        try:
            self._make_request('get', '/status')
            return True
        except:
            return False

    def create_profile(self, name):
        """Create a new browser profile in AdsPower."""
        try:
            data = self._make_request(
                'post',
                ADSPOWER_CREATE_PROFILE,
                json={"name": name, "group_id": "0"}
            )
            
            if data["code"] == 0:
                return data["data"]["id"]
            else:
                logging.error(f"Failed to create profile: {data['msg']}")
                return None
                
        except Exception as e:
            logging.error(f"Error creating AdsPower profile: {str(e)}")
            return None

    def open_browser(self, profile_id):
        """Start browser with specified profile."""
        try:
            data = self._make_request(
                'get',
                ADSPOWER_OPEN_URL,
                params={"user_id": profile_id}
            )
            
            if data["code"] == 0:
                return {
                    "selenium_port": data["data"]["selenium_port"],
                    "debug_port": data["data"]["debug_port"]
                }
            else:
                logging.error(f"Failed to open browser: {data['msg']}")
                return None
                
        except Exception as e:
            logging.error(f"Error opening browser: {str(e)}")
            return None

    def close_browser(self, profile_id):
        """Close browser for specified profile."""
        try:
            data = self._make_request(
                'get',
                ADSPOWER_CLOSE_URL,
                params={"user_id": profile_id}
            )
            return data["code"] == 0
            
        except Exception as e:
            logging.error(f"Error closing browser: {str(e)}")
            return False
