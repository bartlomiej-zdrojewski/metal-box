from flask import Flask
from db.const import *

app = Flask(__name__, static_url_path="")


@app.route("/",  methods=[GET])
def homePage():
    return "OK", 200
