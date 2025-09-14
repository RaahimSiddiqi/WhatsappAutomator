APP_NAME = "WhatsApp Automator"
APP_VERSION = "1.0.0"

WHATSAPP_WEB_URL = "https://web.whatsapp.com"

MESSAGE_INPUT_XPATH = '//div[@contenteditable="true"][@data-tab="10"]'
SEND_BUTTON_XPATH = '//button[@aria-label="Send"]//span[@data-icon="send"]'
LOGIN_CHECK_XPATH = '//div[@data-testid="chat-list"]'
ATTACHMENT_BUTTON_XPATH = '//div[@title="Attach"]//input[@type="file"]'

DEFAULT_TIMEOUT = 30
DEFAULT_MESSAGE_DELAY = 5

PLACEHOLDER_NAME = "%NAME%"
PLACEHOLDER_PHONE = "%PHONE%"
PLACEHOLDER_DATE = "%DATE%"

MAX_MESSAGE_LENGTH = 4096
MAX_ATTACHMENT_SIZE = 16 * 1024 * 1024

SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
SUPPORTED_DOCUMENT_FORMATS = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt"]
SUPPORTED_VIDEO_FORMATS = [".mp4", ".avi", ".mov", ".wmv", ".flv"]

DEFAULT_COUNTRY_CODE = ""

LOG_FILE = "whatsapp_automator.log"
DATA_DIR = "data"
PROFILE_DIR = ".whatsapp_automator"