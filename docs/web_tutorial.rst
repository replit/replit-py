Building Websites and APIs
==========================

.. note:: This guide assumes that you are familiar with running code of some kind on
Replit. If you aren’t, please refer to our
`Quick Start Guide <https://docs.repl.it/misc/quick-start>`_.

In this tutorial, we are you going to build a Web Service – a process
that responds to incoming HTTP Requests, like the ones that come from
web browsers or even API Clients.

`HTTP <https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol>`_, if you aren’t
familiar, is a protocol that allows modern
machines (and users of them) to interoperate. You use HTTP every time
you open an app on your phone that talks with the web. If you can’t
use an app on your phone without internet, it’s because it’s talking
to another computer (a server), mostly likely with HTTP.

The Basics
----------

Code can operate with HTTP in one of two ways:

1. Code can serve HTTP requests: a website
2. Code can consume HTTP responses: a browser

HTTP Requests
~~~~~~~~~~~~~

If you think you aren’t familiar with the concept of an actual HTTP
request, you may be mistaken! Here’s an overt example:

.. image:: _static/404.png

Every HTML page you visit is a distinct HTTP response. However, this one
is remarkable in that it is a 404 page. The ‘404: Not Found’ is known as
the HTTP Status Code.  There’s a full list of them:

`List of HTTP status codes - Wikipedia`_

The relevant ones are divided into four major categories, distinguished
by the first number:

-  ``2xx``: Success!
-  ``3xx``: Redirection — *a URL moved*.
-  ``4xx``: Client Errors — *something went wrong on the consumption side*.
-  ``5xx``: Server Errors — *something went wrong on the server side*.

There’s a well-defined standard that declares these codes, and it is
known as `RFC 2616`_.

.. _List of HTTP status codes - Wikipedia: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
.. _RFC 2616: https://tools.ietf.org/html/rfc2616

Getting started with replit web
-------------------------------

Getting started with the replit web library is simple. It is based on top of the popular
python web framework `Flask <https://flask.palletsprojects.com>`_, with extra features
added in.

Here is the basic code you can run in a `Python repl <https://replit.com/l/python3>`_
to get an HTTP server running:

::

  from replit import web

  app = web.App(__name__)

  @app.route("/")
  def index():
    return "Hello, world!"
  
  app.run()

You should have a website pop up in your repl with the text "Hello, world!"

But what exactly does this code do? Let's go over it line by line.

First, it imports the replit web library. Next, it creates a new "app" object using
the current module name. This tells flask
`where to look <https://flask.palletsprojects.com/en/1.1.x/quickstart/>`_ for static
files and templates.

Next, a new route is added. This uses a 
`python decorator <https://realpython.com/primer-on-python-decorators/>`_ to make the 
function we are defining the handler for the "/" route. This means that when a user
visits the URL of our website, the index function will be called because the URL
matches.

We define a new function called "index" to handle requests to the root of our website.
This function just returns the string "Hello, world!". In flask, there are many types
of data you can return from a handler. If you return a string, that text will be
returned as the response to the request.

Finally, we use the :code:`app.run()` method to start our app. The replit library will
use a configuration suited to running your app so you don't have to worry about hosts
and ports.


Building a simple API
---------------------

To demonstrate a simple API that uses Repl Auth and Database together, let's make a
simple website that counts how many times you visit it.

Let's start with the "Hello, world!" code from above and edit the index route:

::

  @app.route("/")
  def index():
      if web.auth.name:
        return f"You are {web.auth.name}"
      else:
        return "You are not signed in!"


You should now see your repl say that you are not signed in. 

What does this do? Well, :code:`web.auth` (or, :code:`web.request.auth`) is a special
object that represents the state of `Repl Auth <https://docs.repl.it/repls/repl-auth>`_.
Repl auth allows users to log into your site using their repl.it account. With the
replit python library, first-class repl auth support is built in. 

Right now, theres no way for users to log in. To add that, all you have to do is
include :code:`web.sign_in_snippet` in your HTML. This will embed a "Login With Replit"
button in your page:

::

  else:
    return "You are not signed in! {web.sign_in_snippet}"


Now, you should be able to sign in with your repl.it account. If you're having issues,
make sure to disable your cookie blocker on replit.com and your repl's page. Repl auth
doesn't currently work in safari for this reason.

If all goes well, your repl should show your username.

An even easier way to require your users to be signed in is to use the
:code:`web.authenticated` decorator.

It is inserted between the :code:`app.route` decorator and your function. We can change
our code to use this decorator and cut out the if statement entirely:

::

  @app.route("/")
  @web.authenticated
  def index():
    return f"You are {web.auth.name}"

This code functions almost identically to how it did previously. The only difference is
that there is no "You are not signed in!" message, only the sign in button. If you
want to change this, you can pass a keyword argument to the decorator with the same
string we had previously:

::

  @app.route("/")
  # This step is optional, it is to demonstrate how the login page can be customized
  @web.authenticated(login_res = f"You are not signed in! {web.sign_in_snippet}")
  def index():
    return f"You are {web.auth.name}"

Now that we have authentication set up, we can use database to count how many times
each user accesses the page. 

Import the database:

::

  from replit import db, web

Whenever a user visits the page, try to get the amount of times they have visited from
the database. If they've never visited before, assume zero. Next, add one to that value
and store it back in the database. Finally, show the value to the user. 

Here is some code that does that:

::

  @app.route("/")
  @web.authenticated
  def index():
      hits = db.get(web.auth.name, 0) + 1
      db[web.auth.name] = hits
      return f"You have visited this page {hits} times"


You should see the number go up each time you refresh the page.

A second way we could accomplish the same thing is to use a :code:`UserStore`,
which uses a dictionary for each user, allowing us to store more than just one
value in it:

::

  users = web.UserStore()

  @app.route("/")
  @web.authenticated
  def index():
      hits = users.current.get("hits", 0) + 1
      users.current["hits"] = hits
      return f"You have visited this page {hits} times"


To take this project further, an idea is to make a leaderboard of the users who
have requested the page the most times.

Building ReplTweet
==================

As a final project, we will build a twitter clone using the replit library. 

Although this is a full-stack project, meaning it uses javascript in the browser to
make it interactive, this tutorial will only cover how the python backend works.

First, we will start with a basic web app. We will add a static path for our HTML, CSS,
and JS, and a user store to manage our users.

::

  from replit import db, web

  # -- Create & configure Flask application.
  app = web.App(__name__)
  app.static_url_path = "/static"

  users = web.UserStore()

  @app.route("/")
  def index():
      return "Hello"


  app.run()

Next, let's make a home route only for signed in users and make the index route a
landing page for signed-out users. Replace the hello-world route with this code:

::

  # Landing page, only for signed out users
  @app.route("/")
  def index():
      if web.auth.is_authenticated:
          return web.local_redirect("/home")
      return web.render_template("index.html")


  # Home page, only for signed in users
  @app.route("/home")
  def home():
      if not web.auth.is_authenticated:
          return web.local_redirect("/")
      return web.render_template("home.html", name=web.whoami())

You can get these templates and all of the static files from
`my repltweet repl <https://replit.com/@Scoder12/repltweet#main.py>`_.

The index template contains a simple landing page and a repl auth button. Don't worry
about the home page template for now. It has the web app to communicate with our
website, but we need to write the API routes first.



