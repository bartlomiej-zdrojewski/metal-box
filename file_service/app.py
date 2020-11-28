import redis
from flask import Flask, render_template

app = Flask(__name__, static_url_path="")
db = redis.Redis(host="redis_db", port=6379, decode_responses=True)

@app.route("/")
def index():
    return render_template("index.html")
