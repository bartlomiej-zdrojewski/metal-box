from flask import Flask
from api import *
from dto.const import *

GET = "GET"

app = Flask(__name__, static_url_path="")
api = Api()


@app.route("/",  methods=[GET])
def homePage():
    return "OK", 200
