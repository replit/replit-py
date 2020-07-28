"""A basic example of repl auth."""
import simple

app = simple.App("app")


@app.route("/")
def index():
    if simple.signed_in:
        return "Hello " + simple.auth.name
    else:
        return simple.signin()  # optionally: simple.sigin(title="My title")


if __name__ == "__main__":
    app.run()
