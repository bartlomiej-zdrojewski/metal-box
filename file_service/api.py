import uuid
import redis
import os.path
from datetime import datetime
from flask import abort
from dto.const import *
from dto.address import *
from dto.package import *
from dto.person import *
from dto.user import *


class Api:

    def __init__(self):
        self.db = redis.Redis(host="redis_db", port=6379,
                              decode_responses=True)

    def getPackageIdFromSerialNumber(self, serial_number):
        return PACKAGE_PREFIX + serial_number

    def doesPackageExist(self, serial_number):
        if not serial_number:
            return False
        return self.db.exists(self.getPackageIdFromSerialNumber(serial_number))

    def getUserIdFromLogin(self, login):
        return USER_PREFIX + login

    def doesUserExist(self, login):
        if not login:
            return False
        return self.db.exists(USER_PREFIX + login)

    def validateUserAccessToPackage(self, user_login, package_serial_number):
        if not self.doesUserExist(user_login):
            abort(500,
                  "Could not validate user access to package. User does not "
                  "exist (login: {})".format(user_login))
        if not self.doesPackageExist(package_serial_number):
            abort(500,
                  "Could not validate user access to package. Package does not "
                  "exist (serial_number: {})".format(package_serial_number))
        user_id = self.getUserIdFromLogin(user_login)
        package_id = self.getPackageIdFromSerialNumber(package_serial_number)
        if not self.db.hexists(PACKAGE_ID_TO_USER_ID_MAP, package_id):
            abort(500,
                  "Could not validate user access to package. No user match "
                  "the package (user_login: {}, package_serial_number: "
                  "{}).".format(user_login, package_serial_number))
        return user_id == self.db.hget(PACKAGE_ID_TO_USER_ID_MAP, package_id)

    def getPackageDocumentFilePath(self, serial_number):
        if not self.doesPackageExist(serial_number):
            abort(500,
                  "Package does not exist "
                  "(serial_number: {})".format(serial_number))
        file_path = ""
        package_id = self.getPackageIdFromSerialNumber(serial_number)
        package = Package.loadFromData(self.db.get(package_id))
        if package.document_file_path:
            file_path = package.document_file_path
            if not os.path.isfile(file_path):
                file_path = ""
        if not file_path:
            file_path = package.generateDocument()
            self.db.set(package.id, package.toData())
        return file_path

    def registerPackageFromRequest(self, user_login, request):
        if not self.doesUserExist(user_login):
            abort(500,
                  "Could not register package. User does not exist "
                  "(user_login: {})".format(user_login))
        sender_phone_number = request.form.get("sender_phone_number")
        receiver_phone_number = request.form.get("receiver_phone_number")
        image = request.files.get("image")
        if not image:
            abort(500,
                  "Could not register package. Image must not be empty.")
        if not image.filename:
            abort(500,
                  "Could not register package. Image must not be empty.")
        _, image_file_extension = os.path.splitext(image.filename)
        if image_file_extension.lower() not in [".png", ".jpg", ".jpeg"]:
            abort(500, "Could not register package. Image file format is "
                  "unsupported (format: {}). Only PNG and JPG formats are "
                  "supported.".format(image_file_extension))
        serial_number = str(uuid.uuid4()).replace("-", "")
        sender = Person(
            request.form.get("sender_name"),
            request.form.get("sender_surname")
        )
        sender_address = Address(
            request.form.get("sender_street"),
            request.form.get("sender_building_number"),
            request.form.get("sender_apartment_number"),
            request.form.get("sender_postal_code"),
            request.form.get("sender_city"),
            request.form.get("sender_country")
        )
        receiver = Person(
            request.form.get("receiver_name"),
            request.form.get("receiver_surname")
        )
        receiver_address = Address(
            request.form.get("receiver_street"),
            request.form.get("receiver_building_number"),
            request.form.get("receiver_apartment_number"),
            request.form.get("receiver_postal_code"),
            request.form.get("receiver_city"),
            request.form.get("receiver_country")
        )
        image_file_path = "{}image_{}{}".format(
            IMAGE_FILES_DIRECTORY, serial_number, image_file_extension)
        package = Package(
            self.getPackageIdFromSerialNumber(serial_number),
            serial_number,
            datetime.utcnow().isoformat(),
            image_file_path,
            "",
            sender,
            sender_address,
            sender_phone_number,
            receiver,
            receiver_address,
            receiver_phone_number,
            PACKAGE_STATUS_NEW
        )
        package_validation_error = package.validate()
        if package_validation_error:
            abort(500,
                  "Could not register package. Package is invalid. "
                  "{}".format(package_validation_error))
        image.save(image_file_path)
        self.db.set(package.id, package.toData())
        self.db.hset(PACKAGE_ID_TO_USER_ID_MAP, package.id,
                     self.getUserIdFromLogin(user_login))
