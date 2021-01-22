from replit import web

app = web.App(__name__)


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
<a href="/query">Querystring version</a>
</body>
</html>
"""


# custom onerror function
def onerror(missing):
    return f"Missing parameter {missing}"


@app.route("/form", methods=["POST"])
@web.needs_params("param", onerror=onerror)
def form(param):
    return f"The value of param is: {param}"


@app.route("/query")
# source can be form, query, or a dictionary
@web.needs_params("q", src="query", onerror=(lambda p: f"Need query param {p}"))
def query(q):
    return f"The query param is: {q}"


if __name__ == "__main__":
    app.run()
