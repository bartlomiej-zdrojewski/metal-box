import re
from flask import Flask, request, jsonify
from flask.helpers import make_response
from flask_jwt_extended import JWTManager, create_access_token
from flask_cors import CORS, cross_origin
from api import *
from dto.const import *
from dto.address import *
from dto.person import *

app = Flask(__name__, static_url_path="")
app.config["JWT_SECRET_KEY"] = os.environ.get(JWT_SECRET_KEY)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = SESSION_EXPIRATION_TIME
jwt = JWTManager(app)
api = Api()
CORS(app, origins=[
    MAIN_SERVICE_ORIGIN,
    COURIER_SERVICE_ORIGIN],
    allow_headers=["Authorization"],
    supports_credentials=True)


@app.route("/",  methods=[GET])
def homePage():
    return "OK", 200


@app.route("/api/login", methods=[POST])
@cross_origin()
def loginRequest():
    request_error = validateLoginRequest(request)
    if request_error:
        return jsonify(error_message=request_error), 401
    login = request.form.get("login")
    session_id, expiration_date = api.createSession(login)
    access_token = create_access_token(identity=login)
    response = jsonify(redirect_url="/secure")
    response.set_cookie(SESSION_ID_KEY, session_id,
                        expires=expiration_date, secure=True, httponly=True)
    response.set_cookie(JWT_TOKEN_KEY, access_token,
                        expires=expiration_date, secure=True, httponly=False)
    # TODO fix supports_credentials
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response, 200


@app.route("/api/logout", methods=[GET])
@cross_origin()
def logoutRequest():
    session_id = request.cookies.get(SESSION_ID_KEY)
    if not session_id:
        return jsonify(error_message="Session id must not be empty."), 400
    if not api.validateSession(session_id):
        return jsonify(error_message="Session is invalid."), 400
    if not api.destroySession(session_id):
        return jsonify(error_message="Failed to destroy session "
                       "(id: {}).".format(session_id)), 500
    response = jsonify(redirect_url="/login")
    response.set_cookie(SESSION_ID_KEY, "", expires=0,
                        secure=True, httponly=True)
    response.set_cookie(JWT_TOKEN_KEY, "", expires=0,
                        secure=True, httponly=False)
    # TODO fix supports_credentials
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response, 200


@app.route("/api/register", methods=[POST])
@cross_origin()
def registerRequest():
    request_error = validateRegisterRequest(request)
    if request_error:
        return jsonify(error_message=request_error), 400
    api.registerUserFromRequest(request)
    # TODO fix supports_credentials
    response = make_response("Created", 201)
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.route("/api/user/<login>", methods=[GET])
@cross_origin()
def userRequest(login):
    if not api.doesUserExist(login):
        # TODO fix supports_credentials
        response = make_response("Not Found", 404)
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    # TODO fix supports_credentials
    response = make_response("OK", 200)
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


def validateLoginRequest(request):
    login = request.form.get("login")
    password = request.form.get("password")
    if not login:
        return "Login must not be empty."
    if not password:
        return "Password must not be empty."
    if not api.doesUserExist(login):
        return "User does not exists (login: {}).".format(login)
    if not api.validateUser(login, password):
        return "Password is invalid."
    return None


# TODO allow to register couriers
def validateRegisterRequest(request):
    login = request.form.get("login")
    password = request.form.get("password")
    password_repeat = request.form.get("password_repeat")
    if not login:
        return "Login must not be empty."
    if not password:
        return "Password must not be empty."
    if not password_repeat:
        return "Password repeat must not be empty."
    if api.doesUserExist(login):
        return "User already exists (login: {}).".format(login)
    if len(login) < 5:
        return "Login must consist of at least 5 characters."
    if not re.search("^[a-zA-Z]+$", login):
        return "Login may only constist of small and big letters of " \
               "latin alphabet."
    if len(password) < 8:
        return "Password must consist of at least 8 characters."
    if not re.search("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%&*])(.*)$",
                     password):
        return "Password must contain small and big letters, digits and " \
               "special characters (!@#$%&*)."
    if password != password_repeat:
        return "Password repeat does not match the original password."
    person = Person(
        request.form.get("name"),
        request.form.get("surname"),
        request.form.get("birthdate"),
        request.form.get("pesel"))
    person_validation_error = person.validate()
    if person_validation_error:
        return "Personal data is invalid. {}".format(person_validation_error)
    address = Address(
        request.form.get("street"),
        request.form.get("building_number"),
        request.form.get("apartment_number"),
        request.form.get("postal_code"),
        request.form.get("city"),
        request.form.get("country"))
    address_validation_error = address.validate()
    if address_validation_error:
        return "Address data is invalid. {}".format(address_validation_error)
    return None
