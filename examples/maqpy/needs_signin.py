from replit import maqpy

app = maqpy.App(__name__)


@app.route("/")
@needs_signin(login_html=f"Hello! {maqpy.sign_in_snippet}")
def index():
    return "Index function"


# needs_signin can also be called with no args
@app.route("/test")
@needs_signin
def test():
    return "Test function"


if __name__ == "__main__":
    app.run()
