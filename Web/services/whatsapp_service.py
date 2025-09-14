import time
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from models.message import Message
from models.contact import Contact
from config import (
    WHATSAPP_WEB_URL,
    MESSAGE_INPUT_XPATH,
    MESSAGE_INPUT_XPATH_FALLBACK,
    SEND_BUTTON_XPATH,
    MEDIA_SEND_BUTTON_XPATH,
    LOGIN_CHECK_XPATH,
    MEDIA_CAPTION_INPUT_XPATH,
    DEFAULT_TIMEOUT
)

logger = logging.getLogger(__name__)


class WhatsAppService(QObject):
    status_update = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    message_sent = pyqtSignal(str, bool)
    login_required = pyqtSignal()
    logged_in = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.driver: Optional[webdriver.Chrome] = None
        self.is_logged_in = False
        self.profile_dir = Path.home() / ".whatsapp_automator" / "chrome_profile"
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self._stop_requested = False

    def initialize_driver(self) -> bool:
        try:
            self.status_update.emit("Initializing Chrome driver...")

            options = Options()
            options.add_argument(f"--user-data-dir={self.profile_dir}")
            options.add_argument("--profile-directory=Default")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            service = ChromeService(ChromeDriverManager().install())

            self.driver = webdriver.Chrome(
                service=service,
                options=options
            )

            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            self.status_update.emit("Chrome driver initialized successfully")
            return True

        except Exception as e:
            error_msg = f"Failed to initialize driver: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False

    def login(self) -> bool:
        # Check if already logged in
        if self.is_logged_in:
            self.status_update.emit("Already logged in to WhatsApp Web")
            return True

        if not self.driver:
            if not self.initialize_driver():
                return False

        try:
            self.status_update.emit("Opening WhatsApp Web...")
            self.driver.get(WHATSAPP_WEB_URL)

            # Short wait to check if already logged in (from persistent session)
            short_wait = WebDriverWait(self.driver, 10)

            try:
                # First, quickly check if we're already logged in
                short_wait.until(EC.presence_of_element_located((By.XPATH, LOGIN_CHECK_XPATH)))

                # We're already logged in from a previous session!
                self.is_logged_in = True
                self.logged_in.emit()
                self.status_update.emit("Already logged in to WhatsApp Web (session restored)")
                logger.info("User already logged in from persistent session")
                return True

            except TimeoutException:
                # Not logged in, need to scan QR code
                self.login_required.emit()
                self.status_update.emit("Please scan the QR code to login...")
                logger.info("QR code scan required for login")

                # Wait longer for QR code scan (up to 5 minutes)
                wait_long = WebDriverWait(self.driver, 300)

                try:
                    wait_long.until(EC.presence_of_element_located((By.XPATH, LOGIN_CHECK_XPATH)))

                    self.is_logged_in = True
                    self.logged_in.emit()
                    self.status_update.emit("Successfully logged in to WhatsApp Web")
                    logger.info("Successfully logged in after QR code scan")
                    return True

                except TimeoutException:
                    error_msg = "Login timeout - QR code was not scanned within 5 minutes"
                    logger.warning(error_msg)
                    self.error_occurred.emit(error_msg)
                    return False

        except Exception as e:
            error_msg = f"Login failed: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False

    def construct_message_url(self, phone_number: str, country_code: str = "") -> str:
        cleaned_number = ''.join(filter(str.isdigit, phone_number))

        if country_code and not cleaned_number.startswith(country_code):
            cleaned_number = country_code + cleaned_number

        return f"https://web.whatsapp.com/send?phone={cleaned_number}&type=phone_number&app_absent=0"

    def send_message(self, contact: Contact, message: Message, country_code: str = "") -> bool:
        # Ensure we're logged in (will check persistent session first)
        if not self.is_logged_in:
            self.status_update.emit("Checking login status...")
            if not self.login():
                self.error_occurred.emit("Must be logged in to send messages")
                return False

        try:
            personalized_text = message.get_personalized_text(contact.name)

            url = self.construct_message_url(contact.phone, country_code)
            self.status_update.emit(f"Sending message to {contact.name} ({contact.phone})...")

            self.driver.get(url)

            wait = WebDriverWait(self.driver, DEFAULT_TIMEOUT)

            # Try primary message input selector first, then fallback
            try:
                message_box = wait.until(
                    EC.element_to_be_clickable((By.XPATH, MESSAGE_INPUT_XPATH))
                )
            except TimeoutException:
                self.status_update.emit("Trying fallback selector for message input...")
                message_box = wait.until(
                    EC.element_to_be_clickable((By.XPATH, MESSAGE_INPUT_XPATH_FALLBACK))
                )

            time.sleep(1)

            # TODO: Implement attachment sending when ATTACHMENT_BUTTON_XPATH is found
            if message.has_attachments():
                logger.warning("Attachment sending not yet implemented - need attachment button selector")
                # self._send_attachments(message.attachments)
                # time.sleep(1)

            # Clear any existing text first
            message_box.clear()

            # Send message with proper line breaks
            lines = personalized_text.split('\n')
            for i, line in enumerate(lines):
                message_box.send_keys(line)
                if i < len(lines) - 1:
                    message_box.send_keys(Keys.SHIFT + Keys.ENTER)

            # Small delay to ensure message is typed
            time.sleep(0.5)

            # Try to find and click send button
            try:
                send_button = self.driver.find_element(By.XPATH, SEND_BUTTON_XPATH)
                send_button.click()
            except:
                # Try media send button as fallback
                try:
                    send_button = self.driver.find_element(By.XPATH, MEDIA_SEND_BUTTON_XPATH)
                    send_button.click()
                except:
                    # Last resort - press Enter
                    message_box.send_keys(Keys.ENTER)

            self.message_sent.emit(contact.phone, True)
            self.status_update.emit(f"Message sent successfully to {contact.name}")

            time.sleep(2)

            return True

        except Exception as e:
            error_msg = f"Failed to send message to {contact.name}: {str(e)}"
            logger.error(error_msg)
            self.message_sent.emit(contact.phone, False)
            self.error_occurred.emit(error_msg)
            return False

    def _send_attachments(self, attachments: List[str]):
        """
        TODO: Implement when we have the correct selectors.
        Need to find:
        1. ATTACHMENT_BUTTON_XPATH - The paperclip/attachment button
        2. File input element after clicking attachment
        3. Send button for attachments
        """
        logger.warning("Attachment sending not implemented - waiting for correct selectors")
        pass

        # Original implementation for reference:
        # try:
        #     wait = WebDriverWait(self.driver, DEFAULT_TIMEOUT)
        #
        #     attachment_button = wait.until(
        #         EC.element_to_be_clickable((By.XPATH, ATTACHMENT_BUTTON_XPATH))
        #     )
        #     attachment_button.click()
        #
        #     time.sleep(1)
        #
        #     file_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
        #
        #     for attachment_path in attachments:
        #         if Path(attachment_path).exists():
        #             file_input.send_keys(str(Path(attachment_path).absolute()))
        #             time.sleep(1)
        #
        #     send_attachment_button = wait.until(
        #         EC.element_to_be_clickable((By.XPATH, MEDIA_SEND_BUTTON_XPATH))
        #     )
        #     send_attachment_button.click()
        #
        #     time.sleep(2)
        #
        # except Exception as e:
        #     logger.error(f"Failed to send attachments: {str(e)}")
        #     raise

    def send_bulk_messages(self, contacts: List[Contact], message: Message,
                          country_code: str = "", delay: int = 5):
        if not contacts:
            self.error_occurred.emit("No contacts provided")
            return

        total = len(contacts)
        successful = 0
        failed = 0

        for i, contact in enumerate(contacts):
            if self._stop_requested:
                self.status_update.emit("Bulk sending stopped by user")
                break

            progress = int((i / total) * 100)
            self.progress_update.emit(progress)

            if self.send_message(contact, message, country_code):
                successful += 1
            else:
                failed += 1

            if i < total - 1:
                time.sleep(delay)

        self.progress_update.emit(100)
        self.status_update.emit(
            f"Bulk sending completed: {successful} successful, {failed} failed"
        )

    def stop_bulk_sending(self):
        self._stop_requested = True

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self.is_logged_in = False
                self.status_update.emit("Driver closed")
            except Exception as e:
                logger.error(f"Error closing driver: {str(e)}")

    def __del__(self):
        self.close()


class BulkSendWorker(QThread):
    status_update = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    message_sent = pyqtSignal(str, bool)
    completed = pyqtSignal(int, int)

    def __init__(self, service: WhatsAppService, contacts: List[Contact],
                 message: Message, country_code: str = "", delay: int = 5):
        super().__init__()
        self.service = service
        self.contacts = contacts
        self.message = message
        self.country_code = country_code
        self.delay = delay
        self._stop_requested = False

    def run(self):
        total = len(self.contacts)
        successful = 0
        failed = 0

        for i, contact in enumerate(self.contacts):
            if self._stop_requested:
                self.status_update.emit("Bulk sending stopped")
                break

            progress = int(((i + 1) / total) * 100)
            self.progress_update.emit(progress)

            if self.service.send_message(contact, self.message, self.country_code):
                successful += 1
                self.message_sent.emit(contact.phone, True)
            else:
                failed += 1
                self.message_sent.emit(contact.phone, False)

            if i < total - 1 and not self._stop_requested:
                time.sleep(self.delay)

        self.completed.emit(successful, failed)

    def stop(self):
        self._stop_requested = True