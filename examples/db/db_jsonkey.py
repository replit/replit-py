from simple import db


def demo():
    print("Testing json decoding: Setting 'myint' to '5'")
    db["myint"] = "5"
    myint = db.jsonkey("myint", int)
    print("myint + 1 is:", myint.get() + 1)
    del db["myint"]

    # error processing demo
    print("Testing error handling menu:")
    db["test"] = "{"
    print("An error is supposed to happen right now:")
    test = db.jsonkey("test", list)
    print("user set test to:", test.get())
    print("Testing set() method:")
    print("Setting test to range(3)...")
    test.set(list(range(3)))
    print(f"Test is now: {test.get()}")

    # custom default and error supression
    print("Testing automatic error supression: Setting 'test' to 'hello'")
    db["test"] = "hello"

    def get_default():
        print("get_default called, returning 42")
        return 42

    test = db.jsonkey("test", int, get_default=get_default, discard_bad_data=True)
    print("Test is: ", test.get())
    del db["test"]


if __name__ == "__main__":
    demo()
