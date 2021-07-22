# flake8: noqa

import flask
from replit import web

app = flask.Flask(__name__)


@app.route("/")
@web.authenticated(login_res=f"Hello! {web.sign_in_snippet}")
def index():
    return "Index function"


# needs_signin can also be called with no args
@app.route("/test")
@web.authenticated
def test():
    return "Test function"


if __name__ == "__main__":
    web.run_app(app)
