import redis
import uuid
import base64
import dateutil.parser
from datetime import datetime, timedelta
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from flask import abort
from db.const import *
from db.user import *
from db.package import *
from db.mailbox import *


class DatabaseInterface:

    def __init__(self):
        self.db = redis.Redis(host="redis_db", port=6379,
                              decode_responses=True)
        if not self.db.exists(SALT_KEY):
            self.db.set(SALT_KEY, base64.b64encode(
                get_random_bytes(16)).decode())
        self.salt = base64.b64decode(self.db.get(SALT_KEY))
        self.__generateExampleData()

    def getDatabase(self):
        return self.db

    def hashPassword(self, password):
        return base64.b64encode(PBKDF2(password, self.salt, 16, count=1000,
                                       hmac_hash_module=SHA256)).decode()

    def __generateExampleData(self):
        # TODO generate default mailboxes
        pass

    #
    # USER SECTION
    #

    def getUserIdFromLogin(self, login):
        return USER_PREFIX + login

    def doesUserExist(self, login):
        if not login:
            return False
        return self.db.exists(self.getUserIdFromLogin(login))

    def getUser(self, login):
        if not self.doesUserExist(login):
            abort(500, "Could not get the user. The user does not exists "
                  "(login: {}).".format(login))
        user_id = self.getUserIdFromLogin(login)
        return User.loadFromData(self.db.get(user_id))

    def isUserCourier(self, login):
        return self.getUser(login).isCourer()

    def validateUser(self, login, password):
        if not self.doesUserExist(login):
            return False
        user = self.getUser(login)
        password_hash = self.hashPassword(password)
        if password_hash != user.password_hash:
            return False
        return True

    #
    # PACKAGE SECTION
    #

    def getPackageIdFromSerialNumber(self, serial_number):
        return PACKAGE_PREFIX + serial_number

    def doesPackageExist(self, serial_number):
        if not serial_number:
            return False
        return self.db.exists(self.getPackageIdFromSerialNumber(serial_number))

    def getPackage(self, serial_number):
        if not self.doesPackageExist(serial_number):
            abort(500,
                  "Could not get the package. The package does not exist "
                  "(serial_number: {}).".format(serial_number))
        package_id = self.getPackageIdFromSerialNumber(serial_number)
        return Package.loadFromData(self.db.get(package_id))

    def getPackageStatus(self, serial_number):
        return self.getPackage(serial_number).status

    #
    # MAILBOX SECTION
    #

    def getMailboxIdFromCode(self, code):
        return MAILBOX_PREFIX + code

    def doesMailboxExist(self, code):
        if not code:
            return False
        return self.db.exists(self.getMailboxIdFromCode(code))

    def getMailbox(self, code):
        if not self.doesMailboxExist(code):
            abort(500,
                  "Could not get the mailbox. The mailbox does not exist "
                  "(code: {}).".format(code))
        mailbox_id = self.getPackageIdFromSerialNumber(code)
        return Mailbox.loadFromData(self.db.get(mailbox_id))

    #
    # SESSION SECTION
    #

    def createSession(self, user_login):
        if not self.doesUserExist(user_login):
            abort(500,
                  "Could not create a session. The user does not exist "
                  "(user_login: {}).".format(user_login))
        session_id = str(uuid.uuid4()).replace("-", "")
        session_expiration_date = datetime.utcnow(
        ) + timedelta(seconds=SESSION_EXPIRATION_TIME)
        self.db.hset(SESSION_ID_TO_USER_LOGIN_MAP, session_id, user_login)
        self.db.hset(SESSION_ID_TO_SESSION_EXPIRATION_DATE_MAP,
                     session_id, session_expiration_date.isoformat())
        return (session_id, session_expiration_date)

    def validateSession(self, session_id):
        if not session_id:
            return None
        if not self.db.hexists(SESSION_ID_TO_USER_LOGIN_MAP, session_id):
            return None
        if not self.db.hexists(SESSION_ID_TO_SESSION_EXPIRATION_DATE_MAP,
                               session_id):
            abort(500,
                  "Could not validate the session. No expiration date match "
                  "the session ID: {}.".format(session_id))
        session_expiration_date = dateutil.parser.parse(self.db.hget(
            SESSION_ID_TO_SESSION_EXPIRATION_DATE_MAP, session_id))
        if session_expiration_date <= datetime.utcnow():
            if not self.destroySession(session_id):
                abort(500,
                      "Could not destroy the session (ID: {}).".format(
                          session_id))
            return None
        session_expiration_date = datetime.utcnow(
        ) + timedelta(seconds=SESSION_EXPIRATION_TIME)
        self.db.hset(SESSION_ID_TO_SESSION_EXPIRATION_DATE_MAP,
                     session_id, session_expiration_date.isoformat())
        user_login = self.db.hget(SESSION_ID_TO_USER_LOGIN_MAP, session_id)
        return (user_login, session_expiration_date)

    def destroySession(self, session_id):
        if not self.db.hexists(SESSION_ID_TO_USER_LOGIN_MAP, session_id):
            return False
        if not self.db.hexists(SESSION_ID_TO_SESSION_EXPIRATION_DATE_MAP,
                               session_id):
            return False
        self.db.hdel(SESSION_ID_TO_USER_LOGIN_MAP, session_id)
        self.db.hdel(SESSION_ID_TO_SESSION_EXPIRATION_DATE_MAP, session_id)
        return True

    #
    # MAILBOX TOKEN SECTION
    #

    def createMailboxToken(self, user_login, mailbox_code):
        if not self.doesUserExist(user_login):
            abort(500,
                  "Could not create a mailbox token. The user does not exist "
                  "(user_login: {}).".format(user_login))
        if not self.isUserCourier(user_login):
            abort(500,
                  "Could not create a mailbox token. The user is not a courier "
                  "(user_login: {}).".format(user_login))
        mailbox_token = str(uuid.uuid4()).replace("-", "")
        mailbox_token_expiration_date = datetime.utcnow(
        ) + timedelta(seconds=MAILBOX_TOKEN_EXPIRATION_TIME)
        self.db.hset(MAILBOX_TOKEN_TO_MAILBOX_CODE_MAP,
                     mailbox_token, mailbox_code)
        self.db.hset(MAILBOX_TOKEN_TO_COURIER_LOGIN_MAP,
                     mailbox_token, user_login)
        self.db.hset(MAILBOX_TOKEN_TO_MAILBOX_TOKEN_EXPIRATION_DATE_MAP,
                     mailbox_token, mailbox_token_expiration_date.isoformat())
        return (mailbox_token, mailbox_token_expiration_date)

    def validateMailboxToken(self, mailbox_code, mailbox_token):
        if not mailbox_code:
            return None
        if not mailbox_token:
            return None
        if not self.db.hexists(MAILBOX_TOKEN_TO_MAILBOX_CODE_MAP,
                               mailbox_token):
            return None
        if not self.db.hexists(MAILBOX_TOKEN_TO_COURIER_LOGIN_MAP,
                               mailbox_token):
            return None
        if not self.db.hexists(
                MAILBOX_TOKEN_TO_MAILBOX_TOKEN_EXPIRATION_DATE_MAP,
                mailbox_token):
            abort(500,
                  "Could not validate the mailbox token. No expiration date "
                  "match the token: {}.".format(mailbox_token))
        mailbox_token_expiration_date = dateutil.parser.parse(self.db.hget(
            MAILBOX_TOKEN_TO_MAILBOX_TOKEN_EXPIRATION_DATE_MAP, mailbox_token))
        if mailbox_token_expiration_date <= datetime.utcnow():
            if not self.destroyMailboxToken(mailbox_token):
                abort(500,
                      "Could not destroy the mailbox token: {}.".format(
                          mailbox_token))
            return None
        if mailbox_code != self.db.hget(MAILBOX_TOKEN_TO_MAILBOX_CODE_MAP,
                                        mailbox_token):
            return None
        courier_login = self.db.hget(MAILBOX_TOKEN_TO_COURIER_LOGIN_MAP,
                                     mailbox_token)
        return (courier_login, mailbox_token_expiration_date)

    def destroyMailboxToken(self, mailbox_token):
        if not self.db.hexists(MAILBOX_TOKEN_TO_MAILBOX_CODE_MAP,
                               mailbox_token):
            return False
        if not self.db.hexists(MAILBOX_TOKEN_TO_COURIER_LOGIN_MAP,
                               mailbox_token):
            return False
        if not self.db.hexists(
                MAILBOX_TOKEN_TO_MAILBOX_TOKEN_EXPIRATION_DATE_MAP,
                mailbox_token):
            return False
        self.db.hdel(MAILBOX_TOKEN_TO_MAILBOX_CODE_MAP, mailbox_token)
        self.db.hdel(MAILBOX_TOKEN_TO_COURIER_LOGIN_MAP, mailbox_token)
        self.db.hdel(MAILBOX_TOKEN_TO_MAILBOX_TOKEN_EXPIRATION_DATE_MAP,
                     mailbox_token)
        return True
