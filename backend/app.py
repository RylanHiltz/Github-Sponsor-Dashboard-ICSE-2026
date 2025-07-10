from flask import Flask
from api.users import users_bp

app = Flask(__name__)
app.register_blueprint(users_bp)


@app.route("/")
def index():
    return "Hello World!"
