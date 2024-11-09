"""Utility functions for the TikTok Ads login automation."""
import logging
import time
from config import LOG_FORMAT, LOG_FILE, LOG_LEVEL, MAX_RETRIES, RETRY_DELAY, PROFILE_IDS_FILE

def setup_logging():
    """Configure logging settings with enhanced formatting and debug level."""
    # Convert string log level to logging constant
    numeric_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    
    # Log initial setup information
    logging.info("Logging system initialized")
    logging.debug(f"Log level set to: {LOG_LEVEL}")
    logging.debug(f"Log file: {LOG_FILE}")

def read_accounts(filename):
    """Read account credentials from file."""
    accounts = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    try:
                        email, email_pass, tiktok_pass = line.strip().split()
                        accounts.append({
                            'email': email,
                            'email_password': email_pass,
                            'tiktok_password': tiktok_pass
                        })
                    except ValueError as e:
                        logging.error(f"Invalid line format in accounts file: {line.strip()}")
                        logging.error(f"Expected format: email email_password tiktok_password")
        logging.info(f"Successfully loaded {len(accounts)} accounts from {filename}")
        return accounts
    except FileNotFoundError:
        logging.error(f"Accounts file not found: {filename}")
        return []
    except Exception as e:
        logging.error(f"Error reading accounts file: {str(e)}")
        return []

def save_profile_id(email, profile_id):
    """Save created profile ID to file with error handling."""
    try:
        with open(PROFILE_IDS_FILE, 'a') as f:
            f.write(f"{email},{profile_id}\n")
        logging.info(f"Saved profile ID {profile_id} for account {email}")
    except Exception as e:
        logging.error(f"Error saving profile ID: {str(e)}")
        logging.error(f"Email: {email}, Profile ID: {profile_id}")

def retry_operation(operation, *args, **kwargs):
    """Retry an operation with exponential backoff and detailed logging."""
    operation_name = operation.__name__
    logging.debug(f"Starting operation: {operation_name}")
    
    for attempt in range(MAX_RETRIES):
        try:
            logging.debug(f"Attempt {attempt + 1}/{MAX_RETRIES} for operation: {operation_name}")
            result = operation(*args, **kwargs)
            
            if result:
                logging.debug(f"Operation {operation_name} succeeded on attempt {attempt + 1}")
                return result
            else:
                logging.warning(f"Operation {operation_name} returned False on attempt {attempt + 1}")
                
        except Exception as e:
            logging.error(f"Operation {operation_name} failed (attempt {attempt + 1}/{MAX_RETRIES})")
            logging.error(f"Error details: {str(e)}")
        
        if attempt < MAX_RETRIES - 1:
            delay = RETRY_DELAY * (attempt + 1)
            logging.debug(f"Waiting {delay} seconds before next attempt")
            time.sleep(delay)
    
    logging.error(f"Operation {operation_name} failed after {MAX_RETRIES} attempts")
    return None
