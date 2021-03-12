Building Websites and APIs
==========================

.. note:: This guide assumes that you are familiar with running code of some kind on
Replit. If you aren’t, please refer to our
`Quick Start Guide <https://docs.repl.it/misc/quick-start>`_.

In this tutorial, we are you going to build a Web Service – a process
that responds to incoming HTTP Requests, like the ones that come from
web browsers or even API Clients.

`HTTP <https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol>`_, if you aren’t familiar, is a protocol that allows modern
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

Building a website with repl.it
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
<where to look https://flask.palletsprojects.com/en/1.1.x/quickstart/>_ for static
files and templates.

Next, a new route is added. This uses a 
<python decorator https://realpython.com/primer-on-python-decorators/>_ to make the 
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

