"""A basic example of repl auth."""
from replit import maqpy

app = maqpy.App("app")


@app.route("/")
def index():
    if maqpy.signed_in:
        return "Hello " + maqpy.auth.name
    else:
        return maqpy.signin()  # optionally: simple.sigin(title="My title")


if __name__ == "__main__":
    app.run()
