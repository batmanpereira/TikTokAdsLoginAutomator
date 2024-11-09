"""TikTok Ads login automation using Selenium."""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchFrameException
import time
import random
import logging
from config import (
    TIKTOK_ADS_URL, SELECTORS, PAGE_LOAD_TIMEOUT,
    IMPLICIT_WAIT, TYPING_DELAY_MIN, TYPING_DELAY_MAX,
    ACTION_DELAY, MANUAL_CAPTCHA_TIMEOUT
)

class TikTokLogin:
    def __init__(self, selenium_port):
        self.driver = None
        self.selenium_port = selenium_port
        self.setup_driver()

    def setup_driver(self):
        """Initialize Selenium WebDriver."""
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Remote(
            command_executor=f"http://localhost:{self.selenium_port}",
            options=options
        )
        self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        self.driver.implicitly_wait(IMPLICIT_WAIT)

    def humanized_type(self, element, text):
        """Simulate human-like typing with random delays."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(TYPING_DELAY_MIN, TYPING_DELAY_MAX))

    def handle_captcha(self):
        """Handle CAPTCHA by waiting for manual resolution."""
        try:
            # Check if CAPTCHA iframe exists
            logging.info("Checking for CAPTCHA presence...")
            iframe = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, SELECTORS['captcha_iframe']))
            )
            
            if not iframe:
                logging.info("No CAPTCHA detected")
                return True
                
            logging.info("CAPTCHA detected, switching to iframe...")
            self.driver.switch_to.frame(iframe)
            
            # Wait for manual CAPTCHA resolution
            logging.info("Waiting for manual CAPTCHA resolution...")
            start_time = time.time()
            
            while time.time() - start_time < MANUAL_CAPTCHA_TIMEOUT:
                try:
                    # Check if CAPTCHA is still present
                    self.driver.find_element(By.XPATH, SELECTORS['captcha_verify_button'])
                    time.sleep(2)
                except:
                    logging.info("CAPTCHA appears to be solved")
                    return True
            
            logging.error("CAPTCHA resolution timeout exceeded")
            return False
            
        except NoSuchFrameException:
            logging.info("CAPTCHA iframe not found, might not be required")
            return True
        except Exception as e:
            logging.error(f"Error handling CAPTCHA: {str(e)}")
            return False
        finally:
            try:
                self.driver.switch_to.default_content()
            except:
                pass

    def login(self, email, password):
        """Perform TikTok Ads login."""
        try:
            self.driver.get(TIKTOK_ADS_URL)
            time.sleep(ACTION_DELAY)
            
            # Enter email
            email_input = self.driver.find_element(By.XPATH, SELECTORS['email_input'])
            self.humanized_type(email_input, email)
            
            # Enter password
            password_input = self.driver.find_element(By.XPATH, SELECTORS['password_input'])
            self.humanized_type(password_input, password)
            
            # Click login
            login_button = self.driver.find_element(By.XPATH, SELECTORS['login_button'])
            login_button.click()
            
            return True
            
        except Exception as e:
            logging.error(f"Error during login: {str(e)}")
            return False

    def enter_verification_code(self, code):
        """Enter email verification code."""
        try:
            code_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, SELECTORS['verification_code_input']))
            )
            self.humanized_type(code_input, code)
            return True
        except Exception as e:
            logging.error(f"Error entering verification code: {str(e)}")
            return False

    def cleanup(self):
        """Close browser and cleanup."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
