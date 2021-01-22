from replit import web

app = web.App(__name__)


@app.route("/")
@web.authed_ratelimit(
    max_requests=1,  # Number of requests allowed
    period=1,  # Amount of time before counter resets
    login_res=web.Page(body=f"Sign in\n{maqpy.sign_in_snippet}"),
    get_ratelimited_res=(lambda left: f"Too many requests, try again after {left} sec"),
)
def index():
    return "You can request this page once per second"


if __name__ == "__main__":
    app.run()
