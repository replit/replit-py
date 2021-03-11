Building Websites and APIs
==========================

.. note:: This guide assumes that you are familiar with running code of some kind on Replit. If you aren’t, please refer to our `Quick Start Guide <https://docs.repl.it/misc/quick-start>`_.

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

1. Code can serve HTTP requests.
2. Code can consume HTTP responses.

These operations are not mutually exclusive, however. A web applications
can (and often do) perform both operations simultaneously. An example of
this is when a website serving incoming requests makes external calls to
backing APIs it is using to power it’s user experience. You’ll see an
example of this in the working demo we’ll link to in the end!

HTTP Requests
~~~~~~~~~~~~~

If you think you aren’t familiar with the concept of an actual HTTP
request, you may actually be mistaken! Here’s an overt example:

.. image:: _static/404.png

Every HTML page you visit is a distinct HTTP response. However, this one
is remarkable in that it is a 404 page. The ‘404: Not Found’ is known as
the HTTP Status Code.  There’s a full list of them:

`List of HTTP status codes - Wikipedia`_

The relevant ones are divided into four major categories, distinguished
by the first number:

-  ``2xx``: Success!
-  ``3xx``: Redirection — *a URL moved*.
-  ``4xx``:  Client Errors — *something went wrong on the consumption side*.
-  ``5xx``: Server Errors — *something went wrong on the server side*.

There’s a well-defined standard that declares these codes, and it is
known as `RFC 2616`_.

HTTP on Replit
--------------

The process of receiving incoming HTTP requests on Replit is very
straight forward: you simply open a port that is bound to the ``0.0.0.0``
host. That’s it! Replit will automatically give you a domain name, and
the interface will present you with a simple browser window that you can
check your frontend with.

The URL of your application (e.g. ``https://<app-name>.<user-name>.repl.co``) is publicly accessible.

.. _Repl.it: http://repl.it/
.. _List of HTTP status codes - Wikipedia: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
.. _RFC 2616: https://tools.ietf.org/html/rfc2616

.. _code-samples:
.. :ref:`installed <install>`

