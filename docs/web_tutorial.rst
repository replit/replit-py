Building Websites and APIs
==========================

.. note:: 
  This guide assumes that you are familiar with running code of some kind on
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

Setup
-----

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

Copy the the :code:`static/main.css`,  :code:`templates/base.html`, 
:code:`templates/index.html`, and :code:`templates/home.html` files from
`my repltweet repl <https://replit.com/@Scoder12/repltweet#main.py>`_ (again,
this tutorial won't focus on the frontend aspect of the app). You can look into these 
files to see how they work if you want. The HTML files use the Jinja2 templating
engine which renders the HTML on every request inside our flask app. It also uses
JavaScript to make the feed interactive.

The index template contains a simple landing page and a repl auth button. Don't worry
about the home page template for now. It has the web app to communicate with our
website, but we need to write the API routes first.

Adding Tweets
-------------

The first thing we will add is a route to create a tweet. Our user data structure will
look like this:

::

  users["example"] = {
    "tweets": [tweet]
  }

Since we are using a dictionary for each user, we will use a :code:`UserStore` object.
We will only be using a single key, :code:`tweets`, but as an extra challenge, you can
add additional fields like a biography.

This is what each tweet will look like:

::

  tweet = {
    "ts": time.time() * 1000, # UTC in ms, will be used as a unique ID
    "body": "Hello repltweet!", # the body of the tweet
    "likes": ["Scoder12"] # a list of the usernames of the users who liked this tweet
  }


Now, we can add a POST route that handles creating a new tweet for the current user. It
will take a "body" argument which is the content of the tweet.

::

  @app.route("/api/tweet", methods=["POST"])
  @web.params("body")
  def api_tweet(body):
      if len(body) == 0:
          return {"error": "Cannot submit a blank tweet"}, 400

      newtweet = dict(body=body, ts=int(time.time() * 1000), likes=[])
      # Use .get() to handle missing keys
      users.current.get("tweets", []).append(newtweet)

      print(f"{web.whoami()} tweeted: {body!r}")

      return {"success": True}

First, we make sure that the user isn't submitting an empty tweet. Next, we create the
tweet object with the body and the current unix timestamp in milliseconds (multiply by
1000 converts from seconds to milliseconds) which is used as the unique identifier, and
we also add an empty likes array since nobody has liked this tweet yet. Finally, we 
append this tweet to the user's tweet array.

Making the feed
---------------

Next, we will implement the ability to see the latest tweets. We will add a GET route
that returns the latest tweets in JSON format.

::

  @app.route("/api/feed")
  def feed():
    # The username is only stored as the key name, but the client doesn't know the key
    name so add an author field to each tweet
    tweets = []
    for name in users.keys():
        for tweet in users[name].get("tweets", []):
            tweets.append({**tweet, "author": "name"})

    # Sort by time, newest first
    tweets = sorted(tweets, key=(lambda t: t.get("ts", 0)), reverse=True)

    return {"tweets": tweets}

We use a list comprehension to iterate over each user in the database. For each of the
users, we iterate over each of their tweets. We add this tweet to our global tweet
list, but instead of appending the tweet directly, we add an "author" field so that the
client knows who wrote this tweet. The reason why we don't store this in the tweet
object directly is that we can know who wrote the tweet by looking at the username we
found the tweet under. We add this author field in a special way. We could use
:code:`tweet["author"] = name`, but this would write the author field into the
database, which is not what we want. We use the syntax :code:`{ **a, **b }` which means
"combine a and b into a new dictionary". An important point to note is that if the same
key exists in both a and b, it will be overwritten with the value from b. We use this
syntax to send both the tweet data and the author to the client without modifying the
tweet in the database.

Finally, we sort the tweets so that the newest ones are at the top. We use the
:code:`sorted()` function on the tweets with a key argument that tells python how it
should sort the data. We need to do this because python doesn't know how to compare two
tweets. In this case we want to sort by timestamp, so we pass a lambda function as the
key that returns the "ts" (timestamp) from the tweet, or 0 if it doesn't have one.
We also tell sorted that it should sort the tweets in reverse order because normally it
sorts from least at the beginning to greatest at the end, but we want the newest tweets
(the ones with the largest timestamp, since timestamps count up from 0 as time goes on)
to be at the beginning and the oldest tweets (lower timestamps) to be at the bottom. We
could also just wrap the sorted call in :code:`reversed()` which would do the same
thing, but passing :code:`reverse=True` is easier to read.

Adding likes and dislikes
-------------------------

Next, we will add the ability to like a post. We will add a single POST route that will
take an author, timestamp, and whether to like or unlike the tweet, and code that will
add or remove that user from that tweet's likes array. 

Taking the author as an argument is not strictly necessary, but it makes the tweet
easier to find because the server only has to search through a single user's tweets
instead of searching through every tweet every posted.

First, we will implement a function that will find a tweet given the author and
timestamp the client provides.

::

  def find_matching_tweet(author, ts):
      matches = [t for t in users[author].get("tweets", []) if t.get("ts") == ts]
      if len(matches) == 1:
          return matches[0]
      else:
          return None

This function will find all tweets by that author and then filter them to only the ones
that match the timestamp. If there is exactly one match, it will return it, otherwise
it returns None. We can use this in our like route to find a matching tweet. 

Here is the implementation of the like route. It is a bit longer than the other ones:

::

  @app.route("/api/like", methods=["POST"])
  @web.params("author", "ts", "action")
  def like(author, ts, action):
      # validate arguments
      if not ts.isdigit():
          return {"error": "Bad ts"}, 400
      ts = int(ts)
      if action not in ["like", "unlike"]:
          return {"error": "Invalid action"}, 400

      tweet = find_matching_tweet(author, ts)
      if tweet is None:
          return {"error": "Tweet not found"}, 404

      me = web.whoami()
      # Convert to a unique set so we can add and remove and prevent double liking
      likes = set(tweet.get("likes", []))
      if action == "like":
          likes.add(me)
      else:
          likes.discard(me)
      tweet["likes"] = list(likes)

      verb = "liked" if action == "like" else "unliked"
      print(f"{me} {verb} {author}'s tweet, it now has {len(likes)} likes")

      return {"success": True}

First, we validate the arguments. Timestamp is passed to us as a string but we must
convert it to a number. We first use :code:`ts.isdigit()` to ensure that all characters
in the string are numbers so that the server won't error when we call :code:`int(ts)`.
We also ensure that action is a valid action value by checking if it is in a hardcoded
list. Next, we use our :code:`find_matching_tweet` function with the user input to find
the tweet they are trying to like. We also make sure to check the return value and
handle the case where no tweet is found by returning an error to the user. 

Once we have the tweet, we can perform the action. The easiest and safest way is to
convert the likes array into a set. A set is a special datatype that holds multiple
elements but each element must be unique. It's like a dictionary but with only keys
and no values. We can use this to easily add and remove items while also ensuring that
all likes are unique (that is, no one can like a post twice using the same account).
This is better than a regular list because we would have to filter every item if we
wanted to remove a value and we would have to make sure the likes are unique in our
code.

If the user is trying to like the tweet, we use the :code:`add()` method to add their
username to the likes set. Otherwise, we know that they are trying to remove their like
from the tweet so we use the :code:`discard()` method. We could have used the
:code:`remove()` method, but there is an important difference between discard and
remove which is that remove throws a :code:`KeyError` when the item isn't present in
the set, but discard just doesn't modify anything. The discard behavior is what we want
in our app because if a user tries to unlike a post that they never liked in the first
place, we don't want our server to throw an error. 

Finally, we convert the set back to a list because sets are not JSON serializeable and
so they cannot be stored in the database. 

Deleting Tweets
---------------

The last method we will implement is deletion. It will be a POST that accepts an author
and timestamp like like does (possible missed oppurtunity for using the DELETE method).

::

  # This function can go at the top
  def is_mod():
    return web.whoami() in ("Scoder12", "Your_username_here")

  @app.route("/api/delete", methods=["POST"])
  @web.params("author", "ts")
  def delete(author, ts):
      if not ts.isdigit():
          return {"error": "Bad ts"}, 400
      ts = int(ts)

      tweet = find_matching_tweet(author, ts)
      if tweet is None:
          return {"error": "Tweet not found"}, 404

      # Moderators bypass this check, they can delete anything
      if not is_mod() and author != web.whoami():
          print(
              f"{web.whoami()!r} tried to delete tweet by {author!r}: Permission denied"
          )
          return {"error": "Permission denied. This incident has been reported."}, 401

      print(web.whoami(), "deleted a tweet by", author)

      users[author]["tweets"] = [
          t for t in users[author].get("tweets", []) if t != tweet
      ]
      return {"success": True}

First, we define an :code:`is_mod` function. This checks if the current username is in
a hardcoded list of moderators. Be careful when editing the tuple: :code:`("a", )` is a
tuple with a single element while :code:`("a")` is the same as :code:`"a"` which will
give you unexpected and potentially insecure behavior.

This method is very similar to the like endpoint. The timestamp gets parsed and is
passed into the :code:`find_matching_tweet` function, the result of which is checked.
Next, we check if the user has permission to delete this tweet. A user can delete
any tweets that they have authored. Additionally, if :code:`is_mod()` is true, the user
can delete any tweet. We use an if-statement to check this logic and return an error
message if the user tries to delete a tweet that does not fit into these constraints.
Finally, if all checks pass, we filter the author's tweets to only be those that are
not the matched tweet (another way to do this could be to compare each tweet's
timestamp with :code:`ts`).

Adding Ratelimits
-----------------

The final step will be to add a ratelimit to our API. Replit-py allows you to do this
out of the box without writing any of your own code. It uses a decorator that
ratelimits each user individually. Because it relies on usernames to apply the
ratelimit, it also automatically requires login. The reason that we use usernames to
apply ratelimits is that on replit there is no concept of IPs so if we ratelimited
globally one malicious user could ratelimit all users of the app. Ratelimiting based on
usernames works well for our use-case because we require users to sign in anyway.

To apply the ratelimit, you can use the :code:`@web.per_user_ratelimit()` decorator, 
but we want to re-use this decorator on multiple routes so we will assign it to a
variable instead. Now, we can add :code:`@ratelimit` after each :code:`@app.route` line
in our API routes to enforce the ratelimit: 

::

  ratelimit = web.per_user_ratelimit(
    max_requests=60,
    period=60,
    login_res=json.dumps({"error": "Not signed in"}),
    get_ratelimited_res=(
        lambda time_left: json.dumps(
            {"error": f"Wait {time_left:.2f} sec before trying again."}
        )
    ),
  )

  # --snip--

  @app.route("/api/tweet", methods=["POST"])
  @ratelimit
  @web.params("body")
  def api_tweet(body):


This ratelimit has a :code:`max_requests` value of 60 and a :code:`period` value of 60,
which means that every 60 seconds (or 1 minute), users can send 60 requests. This is
almost the same as 1 and 1 but it allows users to use multiple requests in a single
second as long as they don't go over 60 requests. Once they hit 60 requests, a user
will not be able to issue any further requests for the rest of the 60 second period.
Note, since we are re-using the same decorator across multiple routes, the ratelimit is
shared between those routes, meaning a request to :code:`/api/like` and then a request
to :code:`/api/tweet` counts as 2 requests instead of one for each endpoint.


Wrapping Up
-----------

That's it for the repltweet tutorial! Feel free to add any new features that
your can think of and be sure to share them with the community!
