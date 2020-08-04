from replit import maqpy

app = maqpy.App(__name__)


@app.route("/")
@maqpy.needs_sign_in(login_html=f"Hello! {maqpy.sign_in_snippet}")
def index():
    return "Index function"


# needs_signin can also be called with no args
@app.route("/test")
@maqpy.needs_sign_in
def test():
    return "Test function"


if __name__ == "__main__":
    app.run()
