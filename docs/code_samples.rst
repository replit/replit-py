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

Adding Required Replit Login
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this example, we are requiring that a Replit user sign in with their Replit user account in order to see the "Hello, World!":

::

   @app.route("/")
   @web.authenticated
   def index():
      return "Hello, World!"
