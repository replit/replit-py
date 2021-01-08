import json

def pack(o):
    return json.dumps(o).encode('utf-8')

def unpack(s):
    return json.loads(s.decode('utf-8'))

def pack_topic(t):
    return t.encode('ascii')

def unpack_topic(s):
    return s.decode('ascii')