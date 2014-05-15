# -*- coding: utf-8 -*-

from gevent.server import StreamServer


class Server(object):

    def __init__(self, master, addr):
        self.master = master
        self.server = StreamServer((addr, 7776), self.handle)

    def start(self):
        self.server.start()

    def stop(self):
        self.server.stop()

    def handle(self, sock, full):
        addr, port = full
        self.master.new_connection(addr, sock)
