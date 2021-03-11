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

   from replit import web

   app = web.App(__name__)

   @web.needs_sign_in(login_res=f"Hello! {web.login_snippet}")
   def index():
      return "Hello, World!"

   app.run()


Getting a User's Profile Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this next example, we will take the logged in user's profile information and present it in API form:

::

   from replit import web, get_profile

   app = web.App(__name__)

   @web.needs_sign_in(login_res=f"Hello! {web.login_snippet}")
   def index():
      username = web.whoami()

      payload = {}
      payload["greetings"] = True
      payload["profile"] = get_profile(username).as_dict

      return payload

   app.run()

Here's the example API response:

::

   $ curl https://replit-py-code-sample.kennethreitz42.repl.co/
   {
      "greetings": true,
      "profile": {
         "avatar_url": "https://storage.googleapis.com/replit/images/1609937177761_8ce62c49dfd5f0192cff5d3684f78a21.jpeg",
         "bio": "Software Engineer focused on abstractions, reducing cognitive overhead, and Design for Humans.",
         "name": "Kenneth Reitz",
         "username": "kennethreitz42"
      }
   }

Pretty useful!

You could use this to build your own social tools based around the Replit community.


ReplTweet Example
~~~~~~~~~~~~~~~~~

A more fully–fledged example is a Repl we have available known as ReplTweet. It is a Twitter clone!

- `https://repl.it/@kennethreitz42/repltweet <https://repl.it/@kennethreitz42/repltweet>`_
- `https://github.com/replit/example-repltweet <https://github.com/replit/example-repltweet>`_

Check out the Repl and the GitHub repo to see it in action and learn more about how to use
this library to your full advantage!
