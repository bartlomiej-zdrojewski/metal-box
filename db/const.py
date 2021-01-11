GET = "GET"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"

SESSION_ID_KEY = "session-id"
JWT_TOKEN_KEY = "jwt-token"
JWT_SECRET_KEY = "JWT_SECRET"
SESSION_EXPIRATION_TIME = 3600  # TODO 300
MAILBOX_TOKEN_EXPIRATION_TIME = 3600  # TODO 60

SALT_KEY = "salt"
USER_PREFIX = "user_"
PACKAGE_PREFIX = "package_"
MAILBOX_PREFIX = "mailbox_"

SESSION_ID_TO_USER_LOGIN_MAP = "session_id_to_user_login_map"
SESSION_ID_TO_SESSION_EXPIRATION_DATE_MAP = \
    "session_id_to_session_expiration_date_map"
MAILBOX_TOKEN_TO_MAILBOX_CODE_MAP = "mailbox_token_to_mailbox_code_map"
MAILBOX_TOKEN_TO_COURIER_LOGIN_MAP = "mailbox_token_to_courier_login_map"
MAILBOX_TOKEN_TO_MAILBOX_TOKEN_EXPIRATION_DATE_MAP = \
    "mailbox_token_to_mailbox_token_expiration_date_map"
PACKAGE_ID_TO_SENDER_ID_MAP = "package_id_to_sender_id_map"
PACKAGE_ID_TO_COURIER_ID_MAP = "package_id_to_courier_id_map"
PACKAGE_ID_TO_MAILBOX_ID_MAP = "package_id_to_mailbox_id_map"

MAIN_SERVICE_ORIGIN = "https://localhost:8080"
COURIER_SERVICE_ORIGIN = "https://localhost:8081"
MAILBOX_SERVICE_ORIGIN = "https://localhost:8082"
AUTHORIZATION_SERVICE_ORIGIN = "https://localhost:8083"
PACKAGE_SERVICE_ORIGIN = "https://localhost:8084"
AUTHORIZATION_SERVICE_API_URL = AUTHORIZATION_SERVICE_ORIGIN + "/api"
PACKAGE_SERVICE_API_URL = PACKAGE_SERVICE_ORIGIN + "/api"

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

NOTIFIER_NAME_KEY = "notifier_name"
PACKAGE_NOTIFIER = "package_notifier"
NOTIFIER_NAME_LIST = [
    PACKAGE_NOTIFIER
]
