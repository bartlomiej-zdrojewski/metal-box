import re
import os
import redis
from flask import Flask, request, jsonify, send_file
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from api import *
from dto.address import *
from dto.person import *

GET = "GET"
POST = "POST"
JWT_SECRET_KEY = "JWT_SECRET"

app = Flask(__name__, static_url_path="")
app.config["JWT_SECRET_KEY"] = os.environ.get(JWT_SECRET_KEY)
api = Api()
jwt = JWTManager(app)
CORS(app)


@app.route("/",  methods=[GET])
def homePage():
    return "OK", 200


@app.route("/api/package/<serial_number>",  methods=[GET])
@jwt_required
def packageDocumentDownloadRequest(serial_number):
    if not api.doesPackageExist(serial_number):
        return jsonify(error_message="Package does not exists "
                       "(id: {}).".format(id)), 404
    login = get_jwt_identity()
    if not api.validateUserAccessToPackage(login, serial_number):
        return jsonify(error_message="User does not have access to the package "
                       "(user_login: {}, package_serial_number: "
                       "{}).".format(login, serial_number)), 403
    file_path = api.getPackageDocumentFilePath(serial_number)
    return send_file(file_path)


@app.route("/api/package", methods=[POST])
@jwt_required
def packageRegisterRequest():
    request_error = validateRegisterRequest(request)
    if request_error:
        return jsonify(error_message=request_error), 400
    login = get_jwt_identity()
    api.registerPackageFromRequest(login, request)
    return "Created", 201


def validateRegisterRequest(request):
    sender = Person(
        request.form.get("sender_name"),
        request.form.get("sender_surname")
    )
    sender_validation_error = sender.validate(False)
    if sender_validation_error:
        return "Sender's personal data is invalid. " \
               "{}".format(sender_validation_error)
    sender_address = Address(
        request.form.get("sender_street"),
        request.form.get("sender_building_number"),
        request.form.get("sender_apartment_number"),
        request.form.get("sender_postal_code"),
        request.form.get("sender_city"),
        request.form.get("sender_country")
    )
    sender_address_validation_error = sender_address.validate()
    if sender_address_validation_error:
        return "Sender's address data is invalid. " \
               "{}".format(sender_address_validation_error)
    sender_phone_number = request.form.get("sender_phone_number")
    if not sender_phone_number:
        return "Sender's phone number must not be empty."
    if not re.search("^\d{9}$", sender_phone_number):
        return "Sender's phone number must consist of exactly 9 digits."
    receiver = Person(
        request.form.get("receiver_name"),
        request.form.get("receiver_surname")
    )
    receiver_validation_error = receiver.validate(False)
    if receiver_validation_error:
        return "Receiver's personal data is invalid. " \
               "{}".format(receiver_validation_error)
    receiver_address = Address(
        request.form.get("receiver_street"),
        request.form.get("receiver_building_number"),
        request.form.get("receiver_apartment_number"),
        request.form.get("receiver_postal_code"),
        request.form.get("receiver_city"),
        request.form.get("receiver_country")
    )
    receiver_address_validation_error = receiver_address.validate()
    if receiver_address_validation_error:
        return "Receiver's address data is invalid. " \
               "{}".format(receiver_address_validation_error)
    receiver_phone_number = request.form.get("receiver_phone_number")
    if not receiver_phone_number:
        return "Receiver's phone number must not be empty."
    if not re.search("^\d{9}$", receiver_phone_number):
        return "Receiver's phone number must consist of exactly 9 digits."
    image = request.files.get("image")
    if not image:
        return "Image must not be empty."
    if not image.filename:
        return "Image must not be empty."
    _, image_file_extension = os.path.splitext(image.filename)
    if image_file_extension.lower() not in [".png", ".jpg", ".jpeg"]:
        return "Image file format is unsupported (format: {}). Only PNG and " \
               "JPG formats are supported.".format(image_file_extension)
    return None
