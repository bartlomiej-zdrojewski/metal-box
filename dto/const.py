SALT_KEY = "salt"
USER_PREFIX = "user_"
PACKAGE_PREFIX = "package_"

SESSION_ID_TO_USER_LOGIN_MAP = "session_id_to_user_login_map"
SESSION_ID_TO_SESSION_EXPIRATION_DATE_MAP = \
    "session_id_to_session_expiration_date_map"
PACKAGE_ID_TO_USER_ID_MAP = "package_id_to_user_id_map"

MAIN_SERVICE_URL = "https://localhost:8080/"
FILE_SERVICE_API_URL = "https://localhost:8081/api/"
IMAGE_FILES_DIRECTORY = "files/images/"
DOCUMENT_FILES_DIRECTORY = "files/documents/"

PACKAGE_STATUS_NEW = "package_status_new"
PACKAGE_STATUS_IN_MAILBOX = "package_status_in_mailbox"
PACKAGE_STATUS_RECEIVED_FROM_MAILBOX = "package_status_received_from_mailbox"
PACKAGE_STATUS_RECEIVED_FROM_SENDER = "package_status_received_from_sender"
PACKAGE_STATUS_LIST = [
    PACKAGE_STATUS_NEW,
    PACKAGE_STATUS_IN_MAILBOX,
    PACKAGE_STATUS_RECEIVED_FROM_MAILBOX,
    PACKAGE_STATUS_RECEIVED_FROM_SENDER
]
