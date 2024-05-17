### `>>> import replit`

[![Run on Repl.it](https://img.shields.io/badge/run-on_Replit-f26208?logo=replit)](https://repl.it/github/replit/replit-py) [![pypi: replit](https://img.shields.io/pypi/v/replit)](https://pypi.org/project/replit/) [![Read the Docs](https://img.shields.io/readthedocs/replit-py/latest?logo=readthedocs&label=ReadTheDocs)](https://replit-py.readthedocs.io/)

This repository is the home for the `replit` Python package, which provides:

- A fully-featured database client for [Replit DB](https://docs.replit.com/category/databases).
- Tools and utilities for Flask Web Development, including an interface to Replit's User Authetication service
- Replit user profile metadata retrieval (more coming here!).

### Open Source License

This library is licensed under the [ISC License](https://en.wikipedia.org/wiki/ISC_license) and is free for you to use, change, or even profit from!

### Setup

With poetry already setup, you can set up the repl for development with:

```
poetry install
```

### Continuous Integration

Running the database unittests `tests/test_database.py` depends on the repl https://replit.com/@util/database-test-jwt. You'll have access to this repl if you are a Replit employee. There's a secret
contained in that repl which you'll have to set as an environment variable in order to run the unittests.
Once you've done that, run the tests with:

```
poetry run python -m unittest
```
