# -*- coding: utf-8 -*-

from SocketServer import TCPServer, BaseRequestHandler
from socket import AF_INET6


master = None


class V6Server(TCPServer):
    address_family = AF_INET6


class Handler(BaseRequestHandler):

    def handle(self):
        global master
        addr, port = self.client_address[2:]
        master.new_connection(addr, self.request)


class Server(object):

    def __init__(self, master_):
        global master
        master = master_
        self.server = V6Server((master.address, 7776), Handler)

    def start(self):
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()
