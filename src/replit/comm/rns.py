repls = {
    'zabot': {
        'ping': '72b02e5d-c3b3-4c24-bc9b-a6b5b648fb9d',
        'messengertest': '7ebae55f-2935-4f5f-9beb-bbd666fd5c2f',
    },
}

def get_rid(repl_path):
    try:
        _, _, user, slug = repl_path.split('.')
        return repls[user][slug]
    except ValueError:
        return ''
