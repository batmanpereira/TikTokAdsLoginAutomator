"""Main script for TikTok Ads login automation."""
import logging
import sys
from utils import setup_logging, read_accounts, save_profile_id, retry_operation
from ads_power import AdsPowerAPI
from tiktok_login import TikTokLogin
from email_handler import EmailVerification
import time

def process_account(account, adspower_api):
    """Process a single TikTok Ads account."""
    logging.info(f"Processing account: {account['email']}")
    
    # Create AdsPower profile
    profile_id = retry_operation(
        adspower_api.create_profile,
        f"TikTok_{account['email']}"
    )
    
    if not profile_id:
        logging.error("Failed to create AdsPower profile")
        return False
    
    save_profile_id(account['email'], profile_id)
    
    # Open browser
    browser_info = retry_operation(adspower_api.open_browser, profile_id)
    if not browser_info:
        logging.error("Failed to open browser")
        return False
    
    try:
        # Initialize TikTok login handler
        tiktok = TikTokLogin(browser_info['selenium_port'])
        
        # Perform login
        if not retry_operation(
            tiktok.login,
            account['email'],
            account['tiktok_password']
        ):
            logging.error("Failed to perform login")
            return False
        
        # Handle CAPTCHA if present
        if not retry_operation(tiktok.handle_captcha):
            logging.error("Failed to handle CAPTCHA")
            return False
        
        # Handle email verification
        email_handler = EmailVerification(
            account['email'],
            account['email_password']
        )
        
        if not email_handler.connect():
            logging.error("Failed to connect to email")
            return False
        
        verification_code = retry_operation(email_handler.get_verification_code)
        if not verification_code:
            logging.error("Failed to get verification code")
            return False
        
        if not retry_operation(
            tiktok.enter_verification_code,
            verification_code
        ):
            logging.error("Failed to enter verification code")
            return False
        
        logging.info(f"Successfully processed account: {account['email']}")
        return True
        
    except Exception as e:
        logging.error(f"Error processing account: {str(e)}")
        return False
        
    finally:
        # Cleanup
        if 'tiktok' in locals():
            tiktok.cleanup()
        if 'email_handler' in locals():
            email_handler.cleanup()
        adspower_api.close_browser(profile_id)

def main():
    """Main execution function."""
    setup_logging()
    logging.info("Starting TikTok Ads login automation")
    
    # Initialize AdsPower API
    adspower_api = AdsPowerAPI()
    
    # Check if AdsPower is running
    if not adspower_api.check_connection():
        logging.error("AdsPower is not running or not accessible. Please start AdsPower and try again.")
        sys.exit(1)
    
    # Read accounts from file
    accounts = read_accounts("accounts.txt")
    if not accounts:
        logging.error("No accounts found in accounts.txt")
        return
    
    # Process each account
    for account in accounts:
        process_account(account, adspower_api)
        time.sleep(5)  # Delay between accounts
    
    logging.info("Automation completed")

if __name__ == "__main__":
    main()
