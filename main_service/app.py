import os
from flask import Flask, request, url_for, abort, redirect, make_response, render_template
from flask_jwt_extended import JWTManager, create_access_token
from api import *
from dto.const import *

app = Flask(__name__, static_url_path="")
app.config["JWT_SECRET_KEY"] = os.environ.get(JWT_SECRET_KEY)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = SESSION_EXPIRATION_TIME
jwt = JWTManager(app)
api = Api()


@app.route("/", methods=[GET])
def homePage():
    return render_template("home.html")


@app.route("/login", methods=[GET])
def loginPage():
    return render_template("login.html")


@app.route("/register", methods=[GET])
def registerPage():
    return render_template("register.html")


@app.route("/secure", methods=[GET])
def securePage():
    return redirect(url_for('packageListPage'))


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
