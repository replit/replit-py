# flake8: noqa

import flask
from replit import web

app = flask.Flask(__name__)


@app.route("/")
@web.per_user_ratelimit(
    max_requests=1,  # Number of requests allowed
    period=1,  # Amount of time before counter resets
    # Optional sign in page
    login_res=f"Hello, please sign in\n{web.sign_in_snippet}",
    get_ratelimited_res=(lambda left: f"Too many requests, try again after {left} sec"),
)
def index():
    return "You can request this page once per second"


if __name__ == "__main__":
    web.run_app(app)
