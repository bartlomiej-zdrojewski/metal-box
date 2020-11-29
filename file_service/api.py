import redis
import json
import uuid
import os.path
from fpdf import FPDF
from datetime import datetime
from model.package import *

USER_PREFIX = "user_"
PACKAGE_PREFIX = "package_"
PACKAGE_ID_TO_USER_LOGIN_MAP = "package_id_to_user_login_map"
PACKAGE_ID_TO_IMAGE_FILE_PATH_MAP = "package_id_to_image_file_path_map"
PACKAGE_ID_TO_DOCUMENT_FILE_PATH_MAP = "package_id_to_document_file_path_map"
IMAGE_FILES_DIRECTORY = "files/images/"
DOCUMENT_FILES_DIRECTORY = "files/documents/"


class Api:

    def __init__(self):
        self.db = redis.Redis(host="redis_db", port=6379,
                              decode_responses=True)

    def doesPackageExist(self, id):
        if not id:
            return False
        return self.db.exists(PACKAGE_PREFIX + id)

    def doesUserExist(self, login):
        if not login:
            return False
        return self.db.exists(USER_PREFIX + login)

    def doesUserHaveAccessToPackage(self, user_login, package_id):
        if not self.doesPackageExist(package_id):
            raise Exception(
                "Package does not exist (id: {})".format(package_id))
        if not self.db.hexists(PACKAGE_ID_TO_USER_LOGIN_MAP, package_id):
            raise Exception(
                "No login match the package id: {}.".format(package_id))
        return user_login == self.db.hget(PACKAGE_ID_TO_USER_LOGIN_MAP, package_id)

    def getPackageDocumentFilePath(self, id):
        if not self.doesPackageExist(id):
            raise Exception("Package does not exist (id: {})".format(id))
        file_path = ""
        if self.db.hexists(PACKAGE_ID_TO_DOCUMENT_FILE_PATH_MAP, id):
            file_path = self.db.hget(PACKAGE_ID_TO_DOCUMENT_FILE_PATH_MAP, id)
            if not os.path.isfile(file_path):
                file_path = ""
        if not file_path:
            file_path = self.generatePackageDocument(id)
        return file_path

    def registerPackageFromRequest(self, user_login, request):
        if not self.doesUserExist(user_login):
            raise Exception(
                "Could not register package. User does not exist (user_login: {})".format(user_login))
        if not request.files.get("image"):
            raise Exception(
                "Could not register package. Image must not be empty.")
        image_file = request.files["image"]
        if not image_file.filename:
            raise Exception(
                "Could not register package. Image must not be empty.")
        # TODO allow only png, jpg and jpeg
        package_id = str(uuid.uuid4()).replace("-", "")
        sender_address = request.form.get("sender_street") + "\n" + request.form.get(
            "sender_apartment_number") + "\n" + request.form.get("sender_postal_code") + "\n" + request.form.get("sender_country")
        receiver_address = request.form.get("receiver_street") + "\n" + request.form.get(
            "receiver_apartment_number") + "\n" + request.form.get("receiver_postal_code") + "\n" + request.form.get("receiver_country")
        package = Package(
            PACKAGE_PREFIX + package_id,
            datetime.utcnow().isoformat(),
            request.form.get("sender_name"),
            request.form.get("sender_surname"),
            sender_address,
            request.form.get("sender_phone_number"),
            request.form.get("receiver_name"),
            request.form.get("receiver_surname"),
            receiver_address,
            request.form.get("receiver_phone_number")
        )
        _, image_file_extension = os.path.splitext(image_file.filename)
        image_file_path = IMAGE_FILES_DIRECTORY + \
            "image_" + package_id + image_file_extension
        image_file.save(image_file_path)
        self.db.set(package.id, package.serialize())
        self.db.hset(PACKAGE_ID_TO_USER_LOGIN_MAP, package_id, user_login)
        self.db.hset(PACKAGE_ID_TO_IMAGE_FILE_PATH_MAP,
                     package_id, image_file_path)

    # TODO move to package class
    def generatePackageDocument(self, id):
        if not self.doesPackageExist(id):
            raise Exception(
                "Package does not exist (id: {})".format(id))
        if not self.db.hexists(PACKAGE_ID_TO_IMAGE_FILE_PATH_MAP, id):
            raise Exception(
                "No image file path match package id: {}.".format(id))
        package_data = self.db.get(PACKAGE_PREFIX + id)
        package = Package.loadFromJson(json.loads(package_data))
        image_file_path = self.db.hget(PACKAGE_ID_TO_IMAGE_FILE_PATH_MAP, id)
        document_file_path = DOCUMENT_FILES_DIRECTORY + "package_" + id + ".pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        self.__add_table_to_pdf(pdf, package)
        pdf.ln(1)
        pdf.image(image_file_path, w=120)
        pdf.output(document_file_path)
        self.db.hset(PACKAGE_ID_TO_DOCUMENT_FILE_PATH_MAP,
                     id, document_file_path)
        return document_file_path

    # TODO refactor
    def __add_table_to_pdf(self, pdf, package):
        n_cols = 2
        col_width = (pdf.w - pdf.l_margin - pdf.r_margin) / n_cols / 2
        font_size = pdf.font_size
        n_lines = 7
        sender_text = package.sender_name + "\n" + package.sender_surname + \
            "\n" + package.sender_address + "\n" + package.sender_phone_number
        receiver_text = package.receiver_name + "\n" + package.receiver_surname + \
            "\n" + package.receiver_address + "\n" + package.receiver_phone_number
        pdf.cell(col_width, n_lines * font_size, "Nadawca", border=1)
        pdf.multi_cell(col_width, font_size,
                       txt=sender_text, border=1)
        pdf.ln(0)
        pdf.cell(col_width, n_lines * font_size, "Odbiorca", border=1)
        pdf.multi_cell(col_width, font_size,
                       txt=receiver_text, border=1)
