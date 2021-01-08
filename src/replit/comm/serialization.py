import json

def pack(o):
    return json.dumps(o).encode('utf-8')

def unpack(s):
    return json.loads(s.decode('utf-8'))

