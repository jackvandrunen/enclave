# -*- coding: utf-8 -*-

from gevent.server import StreamServer


class Server(object):

    def __init__(self, master):
        self.master = master
        self.server = StreamServer((master.address, 7776), self.handle)

    def start(self):
        self.server.start()

    def stop(self):
        self.server.stop()

    def handle(self, sock, full):
        addr, port = full[:2]
        self.master.new_connection(addr, sock)
