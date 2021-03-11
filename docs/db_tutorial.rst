Replit Database Tutorial
========================

This tutorial will demonstrate the features of the python repl.it database client. 

Quickstart
----------

Repl.it DB is super simple to get up and running. Just use it like a regular python dictionary:

::

   from replit import db

   db["key"] = 12
   print(db["key"]) # => 12

You can list and delete keys the same way you would from a regular python dictionary:

::

   db["a"] = 1
   db["b"] = 2
   print(db.keys()) # => {"a", "b"}

   del db["b"]
   print(db.keys()) # => {"a"}

Other dictionary methods work too:

::

   print(db.get("a")) # => 1
   print(db.get("a key that does not exist", 57)) # => 57

   print(db.pop("a")) # => 1


You can store more than just numbers. The client uses `JSON <https://en.wikipedia.org/wiki/JSON>`_
internally, so any of the JSON types can be stored too:

::

   db["a number"] = 42

   db["nothing"] = None

   db["a list"] = [1, 2, 3]

   db["a dictionary"] = {"a": 1}


The database client also has some convience features for working with these types.
You can mutate lists and dictionaries you get from the database, and your changes will
be persisted!

::

   db["user"] = {"score": 100}
   db["user"]["score"] += 100
   print(db["user"]["score"]) # => 200

   db["friends"] = ["Alice", "Bob"]
   db["friends"].append("Carol")
   print(db["friends"]) # => ["Alice", "Bob", "Carol"]


All of the usual dictionary and list methods are supported.

Finally, you can also find keys based on a prefix:

::

   db["key1"] = 1
   db["key2"] = 2
   db["something else"] = 3
   print(db.keys()) # => {"key1", "key2", "something else"}
   print(db.prefix("key")) # => ("key1", "key2")


Async Usage
-----------

The async client API is very similar to the sync API in terms of method names.

::

   import AsyncDatabase from replit.database

   db = AsyncDatabase()
   await db.set("a", "1")
   await db.get("a") # => "1"

   for i in await db.keys():
      print(i)

   await db.delete("a")

One important difference is dictionary-style usage and nested setting are only available
in the sync library. 

Like the sync library, the async library does JSON encoding and decoding in get and set
but also has get_raw and set_raw methods:

::

   await db.set("a", "val")
   await db.get_raw("a") # => '"val"'

   await db.set_raw("b", '"abc"')
   await db.get("b") # => "abc"

It also has set_bulk and set_bulk_raw for setting multiple keys and values in a single request:

::

   await db.set_bulk({"a": 1, "b": 2, "c": 3})
   await db.get("c") # => 3

   await db.set_bulk_raw({"d": '"abc"'})
   await db.get("d") # => "abc'


Advanced Usage
--------------

For some use-cases you might not want your data to be JSON-encoded. To avoid this, just
use the get_raw and set_raw methods:

::

   db["a"] = "string"
   db.get_raw("a") # => '"a"'

   db.set_raw("a", '"b"')
   db["a"] # => "b"


Another problem you might encounter is related to the mutation feature. Under the hood,
this feature works by replacing the primitive list and dict classes with special
replacements that listen for mutation, namely replit.database.database.ObservedList and
replit.database.ObservedDict. 

To JSON encode these values, use the replit.database.dump method. For JSON responses in
the web framework, this is done automatically. 

To convert these classes to their primitive equivalent, access the value attribute. A
function that automatically does this is provided: replit.database.to_primitive.

