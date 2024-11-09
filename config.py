"""Configuration settings for the TikTok Ads login automation."""
import os

# AdsPower API configuration
ADSPOWER_LOCAL_URL = "http://local.adspower.net:50325"
ADSPOWER_API_URL = "https://959a-2804-58e8-4080-4500-5d27-c43c-e909-bd34.ngrok-free.app"

ADSPOWER_CREATE_PROFILE = "/api/v1/profile/create"
ADSPOWER_OPEN_URL = "/api/v1/browser/start"
ADSPOWER_CLOSE_URL = "/api/v1/browser/stop"
ADSPOWER_TIMEOUT = 10  # Timeout for AdsPower API requests

# TikTok URLs
TIKTOK_ADS_URL = "https://ads.tiktok.com/i18n/login"

# Timeouts and delays (in seconds)
PAGE_LOAD_TIMEOUT = 30
IMPLICIT_WAIT = 10
TYPING_DELAY_MIN = 0.1
TYPING_DELAY_MAX = 0.3
ACTION_DELAY = 2
RETRY_DELAY = 5
MAX_RETRIES = 3
MANUAL_CAPTCHA_TIMEOUT = 300  # 5 minutes timeout for manual CAPTCHA resolution

# Selectors for TikTok Ads page
SELECTORS = {
    'email_input': '//input[@name="email"]',
    'password_input': '//input[@name="password"]',
    'login_button': '//button[@type="submit"]',
    'captcha_iframe': '//iframe[contains(@src, "captcha")]',
    'verification_code_input': '//input[@placeholder="Enter 6-digit code"]',
    'captcha_verify_button': '//button[contains(@class, "verify")]'
}

# Email (IMAP) settings
IMAP_SERVER = "outlook.office365.com"
IMAP_PORT = 993
EMAIL_SEARCH_TIMEOUT = 60
EMAIL_CHECK_INTERVAL = 5

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
LOG_FILE = 'tiktok_login.log'
LOG_LEVEL = 'DEBUG'  # Changed to DEBUG for more detailed logging

# Output files
PROFILE_IDS_FILE = 'profile_ids.txt'
