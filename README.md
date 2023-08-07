### `>>> import replit`

![compute](https://github.com/kennethreitz42/replit-py/blob/kr-cleanup/ext/readme.gif?raw=true)

This repository is the home for the `replit` Python package, which provides:

- A fully-featured database client for [Replit DB](https://docs.repl.it/misc/database).
- A Flask–based application framework for accelerating development on the platform.
- Replit user profile metadata retrieval (more coming here!).
- A simple audio library that can play tones and audio files!

### Open Source License

This library is licensed under the [ISC License](https://en.wikipedia.org/wiki/ISC_license) and is free for you to use, change, or even profit from!

### Setup

With poetry already setup, you can set up the repl for development with:

```
poetry setup
```

### Continuous Integration

Running the database unittests `tests/test_database.py` depends on the repl https://replit.com/@util/database-test-jwt. You'll have access to this repl if you are a Replit employee. There's a secret
contained in that repl which you'll have to set as an environment variable in order to run the unittests.
Once you've done that, run the tests with:

```
poetry run python -m unittest
```