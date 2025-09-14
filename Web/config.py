APP_NAME = "WhatsApp Automator"
APP_VERSION = "1.0.0"

WHATSAPP_WEB_URL = "https://web.whatsapp.com"

# Primary Search Bar Input selector
SEARCH_BAR_INPUT_XPATH = "//div[contains(@class,'lexical-rich-text-input')]//div[@role='textbox' and @contenteditable='true']"

# Primary Message Bar Input selector
MESSAGE_INPUT_XPATH = "//div[contains(@class,'lexical-rich-text-input')]//div[@role='textbox' and @contenteditable='true' and @data-lexical-editor='true' and @tabindex='10' and @data-tab='10' and @aria-owns='emoji-suggestion' and not(ancestor::*[@aria-hidden='true'])]"

# Fallback message input selector
MESSAGE_INPUT_XPATH_FALLBACK = "//div[contains(@class,'lexical-rich-text-input')]//div[@role='textbox' and (@aria-label='Type a message')]"

# Send button selectors
SEND_BUTTON_XPATH = "//button[@aria-label='Send']"
# Media send button (for images/attachments)
MEDIA_SEND_BUTTON_XPATH = "//div[@role='button' and @aria-label='Send']//span[@data-icon='wds-ic-send-filled']"

# Login detection - checks for elements that appear after successful login
# Using contains() to match divs that have these classes, even if there are additional classes
LOGIN_CHECK_XPATH = "//div[@class='x1c4vz4f xs83m0k xdl72j9 x1g77sc7 x78zum5 xozqiw3 x1oa3qoh x12fk4p8 xeuugli x2lwn1j x1nhvcw1 xdt5ytf x1cy8zhl xh8yej3 x5yr21d']"

# TODO: Need to find these selectors from current WhatsApp Web:
# QR_CODE_XPATH = "// NEED SELECTOR FOR QR CODE CANVAS/IMAGE"
# ATTACHMENT_BUTTON_XPATH = "// NEED SELECTOR FOR ATTACHMENT/PAPERCLIP BUTTON"
# CHAT_SEARCH_XPATH = "// NEED SELECTOR FOR SEARCH/FILTER CHATS INPUT"
# NEW_CHAT_BUTTON_XPATH = "// NEED SELECTOR FOR NEW CHAT BUTTON"

# Media input for captions
MEDIA_CAPTION_INPUT_XPATH = "//div[@class='x1hx0egp x6ikm8r x1odjw0f x1k6rcq7 x1lkfr7t']//p"

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