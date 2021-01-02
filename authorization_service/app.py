import re
from flask import Flask, request, jsonify, abort
from flask_jwt_extended import JWTManager, create_access_token
from flask_cors import CORS, cross_origin
from flask_restplus import Api, Resource, fields
from db.dbi import *

app = Flask(__name__, static_url_path="")
app.config["JWT_SECRET_KEY"] = os.environ.get(JWT_SECRET_KEY)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = SESSION_EXPIRATION_TIME
jwt = JWTManager(app)
api = Api(app)
dbi = DatabaseInterface()

CORS(app, origins=[
    MAIN_SERVICE_ORIGIN,
    COURIER_SERVICE_ORIGIN],
    allow_headers=["Authorization"],
    supports_credentials=True)

user_namespace = api.namespace(
    "User",
    path="/api/user",
    description="Authorization Service API")


@user_namespace.route("/<login>")
class UserResource(Resource):

    @cross_origin()
    @api.doc(responses={200: "OK",
                        404: "Not Found"})
    def get(self, login):
        """ Returns "OK" when the user exists and "Not Found" otherwise. """
        if not dbi.doesUserExist(login):
            return "Not Found", 404
        return "OK", 200


@user_namespace.route("/login")
class LoginResource(Resource):

    log_in_form_model = api.model("Log In Form Model", {
        "login": fields.String(
            required=True, description="A login."),
        "password": fields.String(
            required=True, description="A password."),
        "as_courier": fields.String(
            required=False, description="A flag determininig whether user must "
            "be a courier to log in. If true, returns \"Unauthorized\" when "
            "user is not a courier.", default=False)
    })

    @cross_origin(supports_credentials=True)
    @api.expect(log_in_form_model)
    @api.doc(responses={200: "OK",
                        401: "Unauthorized, {error_message: string}"})
    def post(self):
        """ Logs in a user. """
        request_error = self.__validateLoginRequest(request)
        if request_error:
            return jsonify(error_message=request_error), 401
        login = request.form.get("login")
        session_id, expiration_date = dbi.createSession(login)
        access_token = create_access_token(identity=login)
        response = jsonify(redirect_url="/secure")
        response.set_cookie(SESSION_ID_KEY, session_id,
                            expires=expiration_date, secure=True, httponly=True)
        response.set_cookie(JWT_TOKEN_KEY, access_token,
                            expires=expiration_date, secure=True, httponly=False)
        return response, 200

    def __validateLoginRequest(self, request):
        login = request.form.get("login")
        password = request.form.get("password")
        login_as_courier = False
        if "as_courier" in request.form:
            if request.form.get("as_courier").lower() == "true":
                login_as_courier = True
        if not login:
            return "The login must not be empty."
        if not password:
            return "The password must not be empty."
        if not dbi.doesUserExist(login):
            return "The user does not exists (login: {}).".format(login)
        if login_as_courier and not dbi.isUserCourier(login):
            return "The user is not a courier (login: {}).".format(login)
        if not dbi.validateUser(login, password):
            return "The password is invalid."
        return None


@user_namespace.route("/logout")
class LogoutResource(Resource):

    @cross_origin(supports_credentials=True)
    @api.doc(responses={200: "OK",
                        400: "Bad Request, {error_message: string}"})
    def post(self):
        """ Logs out a user. """
        session_id = request.cookies.get(SESSION_ID_KEY)
        if not session_id:
            return jsonify(error_message="The session ID must not "
                           "be empty."), 400
        if not dbi.validateSession(session_id):
            return jsonify(error_message="The session is invalid."), 400
        if not dbi.destroySession(session_id):
            return jsonify(error_message="Failed to destroy the session "
                           "(ID: {}).".format(session_id)), 500
        response = jsonify(redirect_url="/login")
        response.set_cookie(SESSION_ID_KEY, "", expires=0,
                            secure=True, httponly=True)
        response.set_cookie(JWT_TOKEN_KEY, "", expires=0,
                            secure=True, httponly=False)
        return response, 200


@user_namespace.route("/register")
class RegisterResource(Resource):

    register_form_model = api.model("Register Form Model", {
        "login": fields.String(required=True, description="A login."),
        "password": fields.String(required=True, description="A password."),
        "password_repeat": fields.String(
            required=True, description="A password repetition."),
        "name": fields.String(required=True, description="A name."),
        "surname": fields.String(required=True, description="A surname."),
        "birthdate": fields.String(
            required=False, description="A birthdate. Required for regular "
            "users. Optional for couriers."),
        "pesel": fields.String(
            required=False, description="A PESEL. Required for regular users. "
            "Optional for couriers."),
        "street": fields.String(
            required=False, description="A street name (a part of "
            "the address). Required for regular users. Optional for couriers."),
        "building_number": fields.String(
            required=False, description="A building number (a part of "
            "the address). Required for regular users. Optional for couriers."),
        "apartment_number": fields.String(
            required=False, description="An aparment number (a part of "
            "the address). Required for regular users. Optional for couriers."),
        "city": fields.String(
            required=False, description="A city (a part of the address). "
            "Required for regular users. Optional for couriers."),
        "postal_code": fields.String(
            required=False, description="A postal code (a part of "
            "the address). Required for regular users. Optional for couriers."),
        "country": fields.String(
            required=False, description="A country (a part of the address). "
            "Required for regular users. Optional for couriers."),
        "is_courier": fields.String(
            required=False, description="A flag determininig whether user "
            "should be registered as a courier.", default=False)
    })

    @cross_origin()
    @api.expect(register_form_model)
    @api.doc(responses={201: "Created",
                        400: "Bad Request, {error_message: string}"})
    def post(self):
        """ Creates a new user. """
        request_error = self.__validateRegisterRequest(request)
        if request_error:
            return jsonify(error_message=request_error), 400
        self.__registerUserFromRequest(request)
        return "Created", 201

    def __validateRegisterRequest(self, request):
        login = request.form.get("login")
        password = request.form.get("password")
        password_repeat = request.form.get("password_repeat")
        is_courier = False
        if "is_courier" in request.form:
            if request.form.get("is_courier").lower() == "true":
                is_courier = True
        if not login:
            return "The login must not be empty."
        if not password:
            return "The password must not be empty."
        if not password_repeat:
            return "The password repeat must not be empty."
        if dbi.doesUserExist(login):
            return "The user already exists (login: {}).".format(login)
        if len(login) < 5:
            return "The login must consist of at least 5 characters."
        if not re.search("^[a-zA-Z]+$", login):
            return "the login may only constist of small and big letters of " \
                "the latin alphabet."
        if len(password) < 8:
            return "The password must consist of at least 8 characters."
        if not re.search(
                "^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%&*])(.*)$",
                password):
            return "The password must contain small and big letters, digits " \
                "and special characters (!@#$%&*)."
        if password != password_repeat:
            return "The password repeat does not match the original password."
        if is_courier:
            person = Person(
                request.form.get("name"),
                request.form.get("surname"))
            person_validation_error = person.validate(False)
            if person_validation_error:
                return "The personal data is invalid. " \
                    "{}".format(person_validation_error)
        else:
            person = Person(
                request.form.get("name"),
                request.form.get("surname"),
                request.form.get("birthdate"),
                request.form.get("pesel"))
            person_validation_error = person.validate()
            if person_validation_error:
                return "The personal data is invalid. " \
                    "{}".format(person_validation_error)
            address = Address(
                request.form.get("street"),
                request.form.get("building_number"),
                request.form.get("apartment_number"),
                request.form.get("postal_code"),
                request.form.get("city"),
                request.form.get("country"))
            address_validation_error = address.validate()
            if address_validation_error:
                return "The address data is invalid. " \
                    "{}".format(address_validation_error)
        return None

    def __registerUserFromRequest(self, request):
        login = request.form.get("login")
        password = request.form.get("password")
        is_courier = False
        if "is_courier" in request.form:
            if request.form.get("is_courier").lower() == "true":
                is_courier = True
        if not login:
            abort(500,
                  "Could not register an user. The login must not be empty.")
        if not password:
            abort(500,
                  "Could not register an user. The password must not be empty.")
        if dbi.doesUserExist(login):
            abort(500,
                  "Could not register an user. The user already exists "
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
        user = User(
            dbi.getUserIdFromLogin(login),
            login,
            dbi.hashPassword(password),
            person,
            address,
            is_courier)
        user_validation_error = user.validate()
        if user_validation_error:
            abort(500,
                  "Could not register an user. The user is invalid. "
                  "{}".format(user_validation_error))
        dbi.getDatabase().set(user.id, user.toData())
