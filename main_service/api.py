import redis
import dateutil.parser
from datetime import datetime, timedelta
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

    def getUserIdFromLogin(self, login):
        return USER_PREFIX + login

    def doesUserExist(self, login):
        if not login:
            return False
        return self.db.exists(self.getUserIdFromLogin(login))

    def fetchUserPackageList(self, login):
        if not self.doesUserExist(login):
            abort(500,
                  "Could not fetch package list. User does not exists "
                  "(login: {}).".format(login))
        package_list = []
        user_id = self.getUserIdFromLogin(login)
        for package_id in self.db.hkeys(PACKAGE_ID_TO_SENDER_ID_MAP):
            if user_id == self.db.hget(PACKAGE_ID_TO_SENDER_ID_MAP, package_id):
                if not self.db.exists(package_id):
                    abort(500,
                          "Could not fetch package list. One of the packages "
                          "does not exist (id: {}).".format(package_id))
                package = Package.loadFromData(self.db.get(package_id))
                package_register_date = dateutil.parser.parse(
                    package.register_date)
                package_register_date_text = package_register_date.strftime(
                    "%Y-%m-%d %H:%M:%S")
                package_is_deletable = "false"
                if package.status == PACKAGE_STATUS_NEW:
                    package_is_deletable = "true"
                package_list.append({
                    "serial_number": package.serial_number,
                    "register_date": package_register_date_text,
                    "status": package.getStatusText(),
                    "url": FILE_SERVICE_API_URL + "/package/" +
                    package.serial_number,
                    "is_deletable": package_is_deletable
                })
        return package_list

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
        session_expiration_date = datetime.utcnow() + \
            timedelta(seconds=SESSION_EXPIRATION_TIME)
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
