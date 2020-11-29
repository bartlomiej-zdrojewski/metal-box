import os
import re
import redis
from flask import Flask, request, jsonify, send_file
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from api import *

GET = "GET"
POST = "POST"
JWT_SECRET_KEY = "JWT_SECRET"

app = Flask(__name__, static_url_path="")
app.config["JWT_SECRET_KEY"] = os.environ.get(JWT_SECRET_KEY)
api = Api()
jwt = JWTManager(app)


@app.route("/api/package/<id>",  methods=[GET])
@jwt_required
def packageDocumentDownloadRequest(id):
    if not api.doesPackageExist(id):
        return jsonify(error_message="Package does not exists (id: {}).".format(id)), 404
    login = get_jwt_identity()
    if not api.doesUserHaveAccessToPackage(login, id):
        return jsonify(error_message="User does not have access to the package (user_login: {}, package_id: {}).".format(login, id)), 403
    file_path = api.getPackageDocumentFilePath(id)
    return send_file(file_path)


@app.route("/api/package",  methods=[POST])
@jwt_required
def packageRegisterRequest():
    request_error = validateRegisterRequest(request)
    if request_error:
        return jsonify(error_message=request_error), 400
    login = get_jwt_identity()
    print(login, flush=True)
    api.registerPackageFromRequest(login, request)
    return "Created", 201


def validateRegisterRequest(request):
    fields = [
        request.form.get("sender_name"),
        request.form.get("sender_surname"),
        request.form.get("sender_street"),
        request.form.get("sender_apartment_number"),
        request.form.get("sender_postal_code"),
        request.form.get("sender_country"),
        request.form.get("sender_phone_number"),
        request.form.get("receiver_name"),
        request.form.get("receiver_surname"),
        request.form.get("receiver_street"),
        request.form.get("receiver_apartment_number"),
        request.form.get("receiver_postal_code"),
        request.form.get("receiver_country"),
        request.form.get("receiver_phone_number"),
        request.files.get("image")]
    sender_postal_code = fields[4]
    sender_phone_number = fields[6]
    receiver_postal_code = fields[11]
    receiver_phone_number = fields[13]
    image = fields[14]
    for field in fields:
        if not field:
            return "No form field can be left empty. Form fields are: sender_name, sender_surname, " \
                "sender_street, sender_apartment_number, sender_postal_code, sender_country, sender_phone_number, " \
                "receiver_name, receiver_surname, receiver_street, receiver_apartment_number, receiver_postal_code, " \
                "receiver_country, receiver_phone_number, image."
    if not re.search("^\d{2}-\d{3}$", sender_postal_code):
        return "Sender's postal code must match the XX-YYY format."
    if not re.search("^\d{9}$", sender_phone_number):
        return "Sender's phone number must consist of exactly 9 digits."
    if not re.search("^\d{2}-\d{3}$", receiver_postal_code):
        return "Receiver's postal code must match the XX-YYY format."
    if not re.search("^\d{9}$", receiver_phone_number):
        return "Receiver's phone number must consist of exactly 9 digits."
    if not image.filename:
        return "Image must not be empty."
    # TODO allow only png, jpg and jpeg
    return None
