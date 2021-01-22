"""An example of the app.login_wall() feature."""
from replit.web import ReplitApp, Link
from replit.web import auth_info

app = web.ReplitApp(__name__)


def login_page() -> str:
    return "Hello, please sign in to access this page!\n" + web.sign_in_snippet


# this is an example of the arguments, but the exclude kwarg already defaults to this
#  and there is a default handler as well.
app.login_wall(exclude=["/"], handler=login_page)


@app.route("/")
def index() -> str:
    return f"Hello! {web.Link('check out this page', href='/page')}"


@app.route("/page")
def page() -> str:
    return f"Hello {web.auth.name}, if you are reading this you signed in."


if __name__ == "__main__":
    app.run()
