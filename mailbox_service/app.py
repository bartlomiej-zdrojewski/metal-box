from flask import Flask
from flask import Flask, url_for, redirect, render_template
from db.const import *

app = Flask(__name__, static_url_path="")


@app.route("/", methods=[GET])
def homePage():
    return redirect(url_for("sendPage"))


@app.route("/send", methods=[GET])
def sendPage():
    return render_template("send.html")


@app.route("/receive", methods=[GET])
def receivePage():
    return render_template("receive.html")


@app.errorhandler(400)
def badRequestErrorPage(error):
    return render_template("error/400.html", error=error)


@app.errorhandler(403)
def forbiddenErrorPage(error):
    return render_template("error/403.html", error=error)


@app.errorhandler(404)
def notFoundErrorPage(error):
    return render_template("error/404.html", error=error)


@app.errorhandler(500)
def internalServerErrorPage(error):
    return render_template("error/500.html", error=error)
