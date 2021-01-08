import os


def expand(topic):
    topic = topic.strip()

    # @ is a convience prefix to refer to a repl owned by a user
    if topic.startswith("@"):
        return "replit.community." + topic[1:]

    # + is a prefix that indicates the topic is public and its name should
    # be prefixed with the global namespace
    if topic.startswith("+"):
        return "replit.community.{}.{}.{}".format(
            os.environ['REPL_OWNER'].lower(),
            os.environ['REPL_SLUG'],
            topic[1:],
        )

    # Otherwise, don't change the topic 
    return topic

