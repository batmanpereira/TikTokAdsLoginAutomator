"""Email verification handler using IMAP for Outlook."""
import imaplib
import email
import time
import logging
from config import (
    IMAP_SERVER, IMAP_PORT, EMAIL_SEARCH_TIMEOUT,
    EMAIL_CHECK_INTERVAL
)

class EmailVerification:
    def __init__(self, email_address, password):
        self.email_address = email_address
        self.password = password
        self.imap = None

    def connect(self):
        """Establish IMAP connection to Outlook."""
        try:
            self.imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
            self.imap.login(self.email_address, self.password)
            return True
        except Exception as e:
            logging.error(f"Failed to connect to email: {str(e)}")
            return False

    def get_verification_code(self):
        """Retrieve verification code from TikTok email."""
        start_time = time.time()
        
        while time.time() - start_time < EMAIL_SEARCH_TIMEOUT:
            try:
                self.imap.select('INBOX')
                _, messages = self.imap.search(None, '(FROM "noreply@ads.tiktok.com" UNSEEN)')
                
                for msg_num in messages[0].split():
                    _, msg_data = self.imap.fetch(msg_num, '(RFC822)')
                    email_body = email.message_from_bytes(msg_data[0][1])
                    
                    # Extract verification code from email body
                    if email_body.is_multipart():
                        for part in email_body.walk():
                            if part.get_content_type() == "text/plain":
                                content = part.get_payload(decode=True).decode()
                                # Look for 6-digit code in the content
                                import re
                                match = re.search(r'\b\d{6}\b', content)
                                if match:
                                    return match.group(0)
                    else:
                        content = email_body.get_payload(decode=True).decode()
                        match = re.search(r'\b\d{6}\b', content)
                        if match:
                            return match.group(0)
                            
            except Exception as e:
                logging.error(f"Error checking email: {str(e)}")
            
            time.sleep(EMAIL_CHECK_INTERVAL)
            
        return None

    def cleanup(self):
        """Close IMAP connection."""
        if self.imap:
            try:
                self.imap.logout()
            except:
                pass
