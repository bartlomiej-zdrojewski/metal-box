import redis
import json
import uuid
import base64
import dateutil.parser
from datetime import datetime, timedelta
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from flask import abort
from dto.const import *
from dto.address import *
from dto.user import *
from dto.package import *
from dto.person import *


class Api:

    def __init__(self):
        self.db = redis.Redis(host="redis_db", port=6379,
                              decode_responses=True)
        if not self.db.exists(SALT_KEY):
            self.db.set(SALT_KEY, base64.b64encode(
                get_random_bytes(16)).decode())
        self.salt = base64.b64decode(self.db.get(SALT_KEY))

    def hashPassword(self, password):
        return base64.b64encode(PBKDF2(password, self.salt, 16, count=1000,
                                       hmac_hash_module=SHA256)).decode()

    def getUserIdFromLogin(self, login):
        return USER_PREFIX + login

    def doesUserExist(self, login):
        if not login:
            return False
        return self.db.exists(self.getUserIdFromLogin(login))

    def validateUser(self, login, password):
        if not self.doesUserExist(login):
            return False
        user = User.loadFromData(self.db.get(self.getUserIdFromLogin(login)))
        password_hash = self.hashPassword(password)
        if password_hash != user.password_hash:
            return False
        return True

    def registerUserFromRequest(self, request):
        login = request.form.get("login")
        password = request.form.get("password")
        if not login:
            abort(500,
                  "Could not register user. Login must not be empty.")
        if not password:
            abort(500,
                  "Could not register user. Password must not be empty.")
        if self.doesUserExist(login):
            abort(500,
                  "Could not register user. User already exists "
                  "(login: {}).".format(login))
        person = Person(
            request.form.get("name"),
            request.form.get("surname"),
            request.form.get("birthdate"),
            request.form.get("pesel"))
        address = Address(
            request.form.get("street"),
            request.form.get("building_number"),
            request.form.get("apartment_number"),
            request.form.get("postal_code"),
            request.form.get("city"),
            request.form.get("country"))
        # TODO allow to register couriers
        user = User(
            self.getUserIdFromLogin(login),
            login,
            self.hashPassword(password),
            person,
            address,
            False)
        user_validation_error = user.validate()
        if user_validation_error:
            abort(500,
                  "Could not register user. User is invalid. "
                  "{}".format(user_validation_error))
        self.db.set(user.id, user.toData())

    def createSession(self, login):
        if not login:
            abort(500,
                  "Could not create session. Login must not be empty.")
        if not self.doesUserExist(login):
            abort(500,
                  "Could not create session. User does not exist "
                  "(login: {}).".format(login))
        session_id = str(uuid.uuid4()).replace("-", "")
        session_expiration_date = datetime.utcnow(
        ) + timedelta(seconds=SESSION_EXPIRATION_TIME)
        self.db.hset(SESSION_ID_TO_USER_LOGIN_MAP, session_id, login)
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
                  "No expiration date match the session id: "
                  "{}.".format(session_id))
        session_expiration_date = dateutil.parser.parse(self.db.hget(
            SESSION_ID_TO_SESSION_EXPIRATION_DATE_MAP, session_id))
        if session_expiration_date <= datetime.utcnow():
            if not self.destroySession(session_id):
                abort(500,
                      "Failed to destroy session (id: {}).".format(session_id))
            return None
        session_expiration_date = datetime.utcnow(
        ) + timedelta(seconds=SESSION_EXPIRATION_TIME)
        self.db.hset(SESSION_ID_TO_SESSION_EXPIRATION_DATE_MAP,
                     session_id, session_expiration_date.isoformat())
        user_login = self.db.hget(SESSION_ID_TO_USER_LOGIN_MAP, session_id)
        return (session_expiration_date, user_login)

    def destroySession(self, session_id):
        if not self.db.hexists(SESSION_ID_TO_USER_LOGIN_MAP, session_id):
            return False
        if not self.db.hexists(SESSION_ID_TO_SESSION_EXPIRATION_DATE_MAP,
                               session_id):
            abort(500,
                  "No expiration date match the session id: "
                  "{}.".format(session_id))
        self.db.hdel(SESSION_ID_TO_USER_LOGIN_MAP, session_id)
        self.db.hdel(SESSION_ID_TO_SESSION_EXPIRATION_DATE_MAP, session_id)
        return True
