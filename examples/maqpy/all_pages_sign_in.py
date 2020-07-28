"""An example of the all_pages_sign_in() feature."""
from replit import maqpy

app = maqpy.App(__name__)
app.all_pages_sign_in(exclude=["/"])


@app.route("/")
def index() -> str:
    return "Some introduction " + maqpy.Link("check out my page", href="/page")


@app.route("/page")
def page() -> str:
    return "Hello, if you are reading this you signed in."
