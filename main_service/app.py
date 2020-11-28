import re
from datetime import datetime, timedelta
from flask import Flask, request, url_for, abort, jsonify, make_response, render_template
from flask.helpers import make_response
from api import *

GET = "GET"
POST = "POST"
SESSION_ID = "session-id"
SESSION_EXPIRATION_TIME = 30

app = Flask(__name__, static_url_path="")
api = Api(SESSION_EXPIRATION_TIME)


@app.route("/", methods=[GET])
def homePage():
    return render_template("home.html")


@app.route("/login", methods=[GET])
def loginPage():
    return render_template("login.html")


@app.route("/registration", methods=[GET])
def registrationPage():
    return render_template("registration.html")


@app.route("/secure", methods=[GET])
def securePage():
    session_id = request.cookies.get(SESSION_ID)
    validation_result = api.validateSession(session_id)
    if not validation_result:
        abort(401, "Unauthorized")
    login = validation_result[0]
    expiration_date = validation_result[1]
    response = make_response(render_template("secure.html"))
    response.set_cookie(SESSION_ID, session_id, max_age=SESSION_EXPIRATION_TIME,
                        expires=expiration_date, secure=True, httponly=True)
    return response


@app.route("/api/login", methods=[POST])
def loginRequest():
    request_error = validateLoginRequest(request)
    if request_error:
        return jsonify(error_message=request_error), 401
    login = request.form.get("login")
    session_id, expiration_date = api.createSession(login)
    response = jsonify(redirect_url=url_for("securePage"))
    response.set_cookie(SESSION_ID, session_id, max_age=SESSION_EXPIRATION_TIME,
                        expires=expiration_date, secure=True, httponly=True)
    return response, 200


@app.route("/api/logout", methods=[GET])
def logoutRequest():
    session_id = request.cookies.get(SESSION_ID)
    if not session_id:
        return jsonify(error_message="Session id must not be empty."), 400
    if not api.validateSession(session_id):
        return jsonify(error_message="Invalid session."), 400
    if not api.destroySession(session_id):
        abort(500, "Failed to destroy session (id: {}).".format(session_id))
    response = jsonify(redirect_url=url_for("loginPage"))
    response.set_cookie(SESSION_ID, "", max_age=0,
                        expires=0, secure=True, httponly=True)
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

# TODO error pages

# @app.errorhandler(400)
# def page_unauthorized(error):
#    return render_template("errors/400.html", error=error)


# @app.errorhandler(401)
# def page_unauthorized(error):
#    return render_template("errors/401.html", error=error)


# @app.errorhandler(403)
# def page_unauthorized(error):
#    return render_template("errors/401.html", error=error)


# @app.errorhandler(404)
# def page_not_found(error):
#    return render_template("errors/404.html", error=error)


# @app.errorhandler(500)
# def page_not_found(error):
#    return render_template("errors/500.html", error=error)


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
        return "Invalid login or password."
    return None


def validateRegisterRequest(request):
    fields = [
        request.form.get("login"),
        request.form.get("password"),
        request.form.get("password_repeat"),
        request.form.get("name"),
        request.form.get("surname"),
        request.form.get("birthdate"),
        request.form.get("pesel"),
        request.form.get("street"),
        request.form.get("apartment_number"),
        request.form.get("city"),
        request.form.get("postal_code"),
        request.form.get("country")]
    login = fields[0]
    password = fields[1]
    password_repeat = fields[2]
    birthdate = fields[5]
    pesel = fields[6]
    postal_code = fields[10]
    for field in fields:
        if not field:
            return "No form field can be left empty. Form fields are: login, password, password_repeat, name, surname, birthdate, " \
                "pesel, street, apartment_number, city, postal_code, country."
    if api.doesUserExist(login):
        return "User already exists (login: {}).".format(login)
    if len(login) < 5:
        return "Login must consist of at least 5 characters."
    if not re.search("^[a-zA-Z]+$", login):
        return "Login may only constist of small and big letters of latin alphabet."
    if len(password) < 8:
        return "Password must consist of at least 8 characters."
    if not re.search("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%&*])(.*)$", password):
        return "Password must contain small and big letters, digits and special characters (!@#$%&*)."
    if password != password_repeat:
        return "Password repeat does not match the original password."
    if not re.search("^\d{4}-\d{2}-\d{2}$", birthdate):
        return "Birthdate must match the YYYY-MM-DD format."
    try:
        datetime.strptime(birthdate, '%Y-%m-%d')
    except ValueError:
        return "Birthdate must be a valid date."
    if len(pesel) != 11:
        return "PESEL must consist of exactly 11 characters."
    if not re.search("^[0-9]+$", pesel):
        return "PESEL may only consist of digits."
    pesel_checksum = 0
    for i in range(len(pesel) - 1):
        digit = (int(pesel[i]) * ([1, 3, 7, 9])[i % 4]) % 10
        pesel_checksum += digit
    pesel_checksum = (10 - (pesel_checksum % 10)) % 10
    if int(pesel[10]) != pesel_checksum:
        return "PESEL is invalid. Check digit is invalid ({} vs {}).".format(pesel[10], pesel_checksum)
    if not re.search("^\d{2}-\d{3}$", postal_code):
        return "Postal code must match the XX-YYY format."
    return None
