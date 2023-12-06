# flake8: noqa

"""A basic example of repl auth."""

import flask
from replit import web

app = flask.Flask(__name__)


@app.route("/")
def index():
    if web.signed_in:
        return "Hello " + web.auth.name
    else:
        return web.signin()  # optionally: simple.sigin(title="My title")


if __name__ == "__main__":
    web.run(app)
