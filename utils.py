"""Utility functions for the TikTok Ads login automation."""
import logging
import time
from config import LOG_FORMAT, LOG_FILE, MAX_RETRIES, RETRY_DELAY, PROFILE_IDS_FILE

def setup_logging():
    """Configure logging settings."""
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )

def read_accounts(filename):
    """Read account credentials from file."""
    accounts = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                email, email_pass, tiktok_pass = line.strip().split()
                accounts.append({
                    'email': email,
                    'email_password': email_pass,
                    'tiktok_password': tiktok_pass
                })
        return accounts
    except Exception as e:
        logging.error(f"Error reading accounts file: {str(e)}")
        return []

def save_profile_id(email, profile_id):
    """Save created profile ID to file."""
    try:
        with open(PROFILE_IDS_FILE, 'a') as f:
            f.write(f"{email},{profile_id}\n")
    except Exception as e:
        logging.error(f"Error saving profile ID: {str(e)}")

def retry_operation(operation, *args, **kwargs):
    """Retry an operation with exponential backoff."""
    for attempt in range(MAX_RETRIES):
        try:
            result = operation(*args, **kwargs)
            if result:
                return result
        except Exception as e:
            logging.error(f"Operation failed (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
        
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY * (attempt + 1))
    
    return None
