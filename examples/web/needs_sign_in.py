from replit import web

app = web.App(__name__)


@app.route("/")
@web.needs_sign_in(login_res=f"Hello! {web.sign_in_snippet}")
def index():
    return "Index function"


# needs_signin can also be called with no args
@app.route("/test")
@web.needs_sign_in
def test():
    return "Test function"


if __name__ == "__main__":
    app.run()
