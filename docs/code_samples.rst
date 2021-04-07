Code Samples
============

Here are a carefully curated collection of code samples for utilizing the ``replit`` Python library:

Hello, World!
~~~~~~~~~~~~~

Here's a basic "Hello, World!" example, using the web framework provided:

::

   from replit import web

   app = web.App(__name__)

   @app.route("/")
   def index():
      return "Hello, World!"

   app.run()

Requiring Replit Auth
~~~~~~~~~~~~~~~~~~~~~

In this example, we are requiring that a Replit user sign in with their Replit user account in order to see the "Hello, World!":

::

   @app.route("/")
   @web.authenticated
   def index():
      return "Hello, World!"

Accessing replit user info
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   @app.route("/")
   def index():
      if web.signed_in:
         return f"You are {auth.name}"
      return f"You are not signed in {web.sign_in_snippet}"

Combining Replit Auth and Replit Database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:code:`web.UserStore` will map usernames to values in the database.

::

   from replit import db, web

   users = web.UserStore()

   @app.route("/")
   @web.authenticated
   def index():
      # users.current is the same as users[web.auth.name]
      hits = users.current.get("hits", 0) + 1
      users.current["hits"] = hits
      return f"You have visited the page {hits} times"
