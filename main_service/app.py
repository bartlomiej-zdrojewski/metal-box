import os
import re
from datetime import datetime, timedelta
from flask import Flask, request, url_for, abort, jsonify, make_response, render_template
from flask_jwt_extended import JWTManager, create_access_token
from api import *
from dto.address import *
from dto.person import *

GET = "GET"
POST = "POST"
SESSION_ID_KEY = "session-id"
SESSION_EXPIRATION_TIME = 3600  # TODO 300
JWT_SECRET_KEY = "JWT_SECRET"
JWT_TOKEN_KEY = "jwt-token"

app = Flask(__name__, static_url_path="")
app.config["JWT_SECRET_KEY"] = os.environ.get(JWT_SECRET_KEY)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = SESSION_EXPIRATION_TIME
api = Api(SESSION_EXPIRATION_TIME)
jwt = JWTManager(app)


@app.route("/", methods=[GET])
def homePage():
    return render_template("home.html")


@app.route("/login", methods=[GET])
def loginPage():
    return render_template("login.html")


@app.route("/register", methods=[GET])
def registerPage():
    return render_template("register.html")


# TODO (8) add option to delete package when it's still new
# TODO (9) remember to delete images and PDFs
@app.route("/secure/package/list", methods=[GET])
def packageListPage():
    user_login = request.environ["secure_user_login"]
    package_list = api.fetchUserPackageList(user_login)
    return make_response(render_template(
        "secure/package-list.html",
        package_list=package_list,
        package_count=len(package_list)
    ))


@app.route("/secure/package/register", methods=[GET])
def packageRegisterPage():
    # TODO autofill, get user data
    return make_response(render_template("secure/package-register.html"))


@app.route("/secure/logout", methods=[GET])
def logoutPage():
    return make_response(render_template("secure/logout.html"))


@app.route("/api/login", methods=[POST])
def loginRequest():
    request_error = validateLoginRequest(request)
    if request_error:
        return jsonify(error_message=request_error), 401
    login = request.form.get("login")
    session_id, expiration_date = api.createSession(login)
    access_token = create_access_token(identity=login)
    response = jsonify(redirect_url=url_for("packageListPage"))
    response.set_cookie(SESSION_ID_KEY, session_id,
                        expires=expiration_date, secure=True, httponly=True)
    response.set_cookie(JWT_TOKEN_KEY, access_token,
                        expires=expiration_date, secure=True, httponly=False)
    return response, 200


@app.route("/api/logout", methods=[GET])
def logoutRequest():
    session_id = request.cookies.get(SESSION_ID_KEY)
    if not session_id:
        return jsonify(error_message="Session id must not be empty."), 400
    if not api.validateSession(session_id):
        return jsonify(error_message="Session is invalid."), 400
    if not api.destroySession(session_id):
        return jsonify(error_message="Failed to destroy session "
                       "(id: {}).".format(session_id)), 500
    response = jsonify(redirect_url=url_for("loginPage"))
    response.set_cookie(SESSION_ID_KEY, "", expires=0,
                        secure=True, httponly=True)
    response.set_cookie(JWT_TOKEN_KEY, "", expires=0,
                        secure=True, httponly=False)
    return response, 200


@app.route("/api/register", methods=[POST])
def registerRequest():
    request_error = validateRegisterRequest(request)
    if request_error:
        return jsonify(error_message=request_error), 400
    api.registerUserFromRequest(request)
    return "Created", 201


@app.route("/api/user/<login>", methods=[GET])
def userRequest(login):
    if not api.doesUserExist(login):
        return "Not Found", 404
    return "OK", 200


@app.before_request
def before_request():
    if request.path.startswith("/secure"):
        session_id = request.cookies.get(SESSION_ID_KEY)
        validation_result = api.validateSession(session_id)
        if not validation_result:
            request.environ["secure_session_id"] = session_id
            request.environ["secure_session_valid"] = False
            abort(401)
        request.environ["secure_session_id"] = session_id
        request.environ["secure_session_valid"] = True
        request.environ["secure_session_expiration_date"] = validation_result[0]
        request.environ["secure_user_login"] = validation_result[1]


@app.after_request
def after_request(response):
    if request.path.startswith("/secure"):
        if request.environ["secure_session_valid"]:
            session_id = request.environ["secure_session_id"]
            session_expiration_date = request.environ[
                "secure_session_expiration_date"]
            user_login = request.environ["secure_user_login"]
            access_token = create_access_token(identity=user_login)
            response.set_cookie(SESSION_ID_KEY, session_id,
                                expires=session_expiration_date,
                                secure=True, httponly=True)
            response.set_cookie(JWT_TOKEN_KEY, access_token,
                                expires=session_expiration_date,
                                secure=True, httponly=False)
    return response


@app.errorhandler(400)
def badRequestErrorPage(error):
    return render_template("error/400.html", error=error)


@app.errorhandler(401)
def unauthorizedErrorPage(error):
    return render_template("error/401.html", error=error)


@app.errorhandler(403)
def forbiddenErrorPage(error):
    return render_template("error/403.html", error=error)


@app.errorhandler(404)
def notFoundErrorPage(error):
    return render_template("error/404.html", error=error)


@app.errorhandler(500)
def internalServerErrorPage(error):
    return render_template("error/500.html", error=error)


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
        request.form.get("country")
    )
    address_validation_error = address.validate()
    if address_validation_error:
        return "Address data is invalid. {}".format(address_validation_error)
    return None
