import redis
import json
import uuid
import base64
import dateutil.parser
from datetime import datetime, timedelta
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from model.user import *
from model.package import *

SALT = "salt"
USER_PREFIX = "user_"
PACKAGE_PREFIX = "package_"
SESSION_ID_TO_LOGIN_MAP = "session_id_to_login_map"
SESSION_ID_TO_EXPIRATION_DATE_MAP = "session_id_to_expiration_date_map"
PACKAGE_ID_TO_USER_LOGIN_MAP = "package_id_to_user_login_map"
FILES_SERVICE_API_URL = "https://localhost:8081/api/"


class Api:

    def __init__(self, session_expiration_time):
        self.session_expiration_time = session_expiration_time
        self.db = redis.Redis(host="redis_db", port=6379,
                              decode_responses=True)
        if not self.db.exists(SALT):
            self.db.set(SALT, base64.b64encode(get_random_bytes(16)).decode())
        self.salt = base64.b64decode(self.db.get(SALT))

    def createSession(self, login):
        if not login:
            raise Exception(
                "Could not create session. Login must not be empty.")
        if not self.doesUserExist(login):
            raise Exception(
                "Could not create session. User does not exist (login: {}).".format(login))
        session_id = str(uuid.uuid4()).replace("-", "")
        expiration_date = datetime.utcnow() + timedelta(seconds=self.session_expiration_time)
        self.db.hset(SESSION_ID_TO_LOGIN_MAP, session_id, login)
        self.db.hset(SESSION_ID_TO_EXPIRATION_DATE_MAP,
                     session_id, expiration_date.isoformat())
        return (session_id, expiration_date)

    def validateSession(self, session_id):
        if not session_id:
            return None
        if not self.db.hexists(SESSION_ID_TO_LOGIN_MAP, session_id):
            return None
        if not self.db.hexists(SESSION_ID_TO_EXPIRATION_DATE_MAP, session_id):
            raise Exception(
                "No expiration date match the session id: {}.".format(session_id))
        expiration_date = dateutil.parser.parse(self.db.hget(
            SESSION_ID_TO_EXPIRATION_DATE_MAP, session_id))
        if expiration_date <= datetime.utcnow():
            if not self.destroySession(session_id):
                raise Exception(
                    "Failed to destroy session (id: {}).".format(session_id))
            return None
        expiration_date = datetime.utcnow() + timedelta(seconds=self.session_expiration_time)
        self.db.hset(SESSION_ID_TO_EXPIRATION_DATE_MAP,
                     session_id, expiration_date.isoformat())
        login = self.db.hget(SESSION_ID_TO_LOGIN_MAP, session_id)
        return (login, expiration_date)

    def destroySession(self, session_id):
        if not self.db.hexists(SESSION_ID_TO_LOGIN_MAP, session_id):
            return False
        if not self.db.hexists(SESSION_ID_TO_EXPIRATION_DATE_MAP, session_id):
            raise Exception(
                "No expiration date match the session id: {}.".format(session_id))
        self.db.hdel(SESSION_ID_TO_LOGIN_MAP, session_id)
        self.db.hdel(SESSION_ID_TO_EXPIRATION_DATE_MAP, session_id)
        return True

    def doesUserExist(self, login):
        if not login:
            return False
        return self.db.exists(USER_PREFIX + login)

    def validateUser(self, login, password):
        if not self.doesUserExist(login):
            return False
        password_hash = self.hashPassword(password)
        user_data = self.db.get(USER_PREFIX + login)
        user = User.loadFromJson(json.loads(user_data))
        if password_hash != user.password_hash:
            return False
        return True

    def getUserPackageList(self, login):
        if not self.doesUserExist(login):
            raise Exception(
                "Could not get package list. User does not exists (login: {}).".format(login))
        package_list = []
        for id in self.db.hkeys(PACKAGE_ID_TO_USER_LOGIN_MAP):
            if login == self.db.hget(PACKAGE_ID_TO_USER_LOGIN_MAP, id):
                if not self.db.exists(PACKAGE_PREFIX + id):
                    continue
                package_data = self.db.get(PACKAGE_PREFIX + id)
                # TODO delete try except block
                try:
                    package = Package.loadFromJson(json.loads(package_data))
                except:
                    continue
                package_list.append({
                    "id": id,
                    "creation_date": package.creation_date,
                    "document_url": FILES_SERVICE_API_URL + "package/" + id
                })
        return package_list

    def registerUserFromRequest(self, request):
        login = request.form.get("login")
        password = request.form.get("password")
        if not login:
            raise Exception(
                "Could not register user. Login must not be empty.")
        if not password:
            raise Exception(
                "Could not register user. Password must not be empty.")
        if self.doesUserExist(login):
            raise Exception(
                "Could not register user. User already exists (login: {}).".format(login))
        id = USER_PREFIX + login
        password_hash = self.hashPassword(password)
        user = User(
            id,
            login,
            password_hash,
            request.form.get("name"),
            request.form.get("surname"),
            request.form.get("birthdate"),
            request.form.get("pesel"),
            request.form.get("street"),
            request.form.get("apartment_number"),
            request.form.get("city"),
            request.form.get("country"))
        self.db.set(user.id, user.serialize())

    def hashPassword(self, password):
        return base64.b64encode(PBKDF2(password, self.salt, 16, count=1000, hmac_hash_module=SHA256)).decode()
