from wsgiref.simple_server import WSGIServer, make_server
from SocketServer import ThreadingMixIn


class ThreadingWSGIServer(WSGIServer, ThreadingMixIn):
    """Because threading"""


def run(app, host, port):
    """Start up a freshly baked server"""
    server = make_server(host, port, app)
    server.serve_forever()
