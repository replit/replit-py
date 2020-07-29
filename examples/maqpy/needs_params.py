from replit import maqpy

app = maqpy.App(__name__)


@app.route("/")
def index():
    return """
<html>
<head><title>Form testing</title></head>
<body>
<h3>Form testing</h3>
<form action="/form" method=POST>
    <button type=submit>Submit form with no parameter</button>
</form>
<form action="/form" method=POST>
    <input type=hidden name=param value=value>
    <button type=submit>Submit form with parameter</button>
</form>
</body>
</html>
"""


# custom onerror function
def onerror(missing):
    return f"Missing parameter {missing}"


@app.route("/form", methods=["POST"])
@maqpy.needs_params("param", onerror=onerror)
def form(param):
    return f"The value of param is: {param}"


if __name__ == "__main__":
    app.run()
