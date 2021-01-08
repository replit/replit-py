import json
import base64

def pack(o):
    return json.dumps(o).encode('utf-8')

def unpack(s):
    return json.loads(s.decode('utf-8'))

def pack_topic(t):
    return t.encode('ascii')

def unpack_topic(s):
    return s.decode('ascii')

def pack_service_name(s):
    base64.b64encode(s.encode('ascii')).decode('ascii')
