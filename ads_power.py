"""AdsPower API integration for browser profile management."""
import requests
import logging
import time
import socket
import json
from urllib.parse import urljoin
from config import (
    ADSPOWER_API_URL, ADSPOWER_LOCAL_URL, ADSPOWER_CREATE_PROFILE,
    ADSPOWER_OPEN_URL, ADSPOWER_CLOSE_URL,
    ADSPOWER_TIMEOUT, MAX_RETRIES, RETRY_DELAY
)

class AdsPowerAPI:
    def __init__(self):
        self.base_url = ADSPOWER_API_URL
        self.local_url = ADSPOWER_LOCAL_URL
        self.session = requests.Session()

    def _check_port_status(self, host='local.adspower.net', port=50325):
        """Check if AdsPower port is open and accessible."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            logging.error(f"Port check failed: {str(e)}")
            return False

    def _log_request_details(self, method, url, **kwargs):
        """Log detailed request information."""
        logging.debug(f"Request Details:")
        logging.debug(f"Method: {method}")
        logging.debug(f"URL: {url}")
        if 'params' in kwargs:
            logging.debug(f"Query Params: {kwargs['params']}")
        if 'json' in kwargs:
            logging.debug(f"Request Body: {json.dumps(kwargs['json'], indent=2)}")
        if 'headers' in kwargs:
            logging.debug(f"Headers: {kwargs['headers']}")

    def _log_response_details(self, response):
        """Log detailed response information."""
        try:
            logging.debug(f"Response Details:")
            logging.debug(f"Status Code: {response.status_code}")
            logging.debug(f"Response Headers: {dict(response.headers)}")
            logging.debug(f"Response Body: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            logging.error(f"Failed to log response details: {str(e)}")

    def _make_request(self, method, endpoint, **kwargs):
        """Make HTTP request to AdsPower API with retries and enhanced error handling."""
        kwargs.setdefault('timeout', ADSPOWER_TIMEOUT)

        # Try ngrok URL first, fallback to local if it fails
        urls_to_try = [self.base_url, self.local_url]
        
        for base_url in urls_to_try:
            url = urljoin(base_url, endpoint)
            self._log_request_details(method, url, **kwargs)
            
            for attempt in range(MAX_RETRIES):
                try:
                    # Check port status before making request
                    if not self._check_port_status():
                        logging.error(f"AdsPower port is not accessible (attempt {attempt + 1}/{MAX_RETRIES})")
                        if attempt < MAX_RETRIES - 1:
                            time.sleep(RETRY_DELAY * (attempt + 1))
                            continue
                        break  # Try next URL if available

                    # Make the request
                    response = self.session.request(method, url, **kwargs)
                    
                    # Log response details
                    self._log_response_details(response)

                    if response.status_code == 200:
                        return response.json()
                    else:
                        logging.error(f"Request failed with status code {response.status_code}")
                        logging.error(f"Response content: {response.text}")
                        
                except requests.exceptions.Timeout:
                    logging.error(f"Request timed out (attempt {attempt + 1}/{MAX_RETRIES})")
                except requests.exceptions.ConnectionError as e:
                    logging.error(f"Connection error (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
                except json.JSONDecodeError as e:
                    logging.error(f"Invalid JSON response (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
                except Exception as e:
                    logging.error(f"Unexpected error (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
                
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
        
        raise Exception("Failed to connect to AdsPower API after multiple retries")

    def check_connection(self):
        """Check if AdsPower is running and accessible with detailed diagnostics."""
        logging.info("Checking AdsPower connection status...")
        
        # Check port status
        if not self._check_port_status():
            logging.error("AdsPower port check failed - service might not be running")
            return False

        try:
            response = self._make_request('get', '/status')
            if response.get("code") == 0:
                logging.info("AdsPower service is running and accessible")
                return True
            else:
                logging.error(f"AdsPower service check failed: {response.get('msg', 'Unknown error')}")
                return False
        except Exception as e:
            logging.error(f"AdsPower connection check failed: {str(e)}")
            logging.error("Please ensure AdsPower is running and accessible")
            return False

    def create_profile(self, name):
        """Create a new browser profile in AdsPower."""
        logging.info(f"Creating new AdsPower profile: {name}")
        try:
            data = self._make_request(
                'post',
                ADSPOWER_CREATE_PROFILE,
                json={"name": name, "group_id": "0"}
            )
            
            if data["code"] == 0:
                profile_id = data["data"]["id"]
                logging.info(f"Successfully created profile with ID: {profile_id}")
                return profile_id
            else:
                logging.error(f"Failed to create profile: {data.get('msg', 'Unknown error')}")
                return None
                
        except Exception as e:
            logging.error(f"Error creating AdsPower profile: {str(e)}")
            return None

    def open_browser(self, profile_id):
        """Start browser with specified profile."""
        logging.info(f"Opening browser for profile: {profile_id}")
        try:
            data = self._make_request(
                'get',
                ADSPOWER_OPEN_URL,
                params={"user_id": profile_id}
            )
            
            if data["code"] == 0:
                browser_info = {
                    "selenium_port": data["data"]["selenium_port"],
                    "debug_port": data["data"]["debug_port"]
                }
                logging.info(f"Successfully opened browser: {browser_info}")
                return browser_info
            else:
                logging.error(f"Failed to open browser: {data.get('msg', 'Unknown error')}")
                return None
                
        except Exception as e:
            logging.error(f"Error opening browser: {str(e)}")
            return None

    def close_browser(self, profile_id):
        """Close browser for specified profile."""
        logging.info(f"Closing browser for profile: {profile_id}")
        try:
            data = self._make_request(
                'get',
                ADSPOWER_CLOSE_URL,
                params={"user_id": profile_id}
            )
            success = data["code"] == 0
            if success:
                logging.info(f"Successfully closed browser for profile: {profile_id}")
            else:
                logging.error(f"Failed to close browser: {data.get('msg', 'Unknown error')}")
            return success
            
        except Exception as e:
            logging.error(f"Error closing browser: {str(e)}")
            return False
