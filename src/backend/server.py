# -*- coding: utf-8 -*-

from gevent.server import StreamServer

import netifaces


class Server(object):

    @staticmethod
    def get_address():
        'Returns the address that we care about, or None'
        ifaces = [i for i in netifaces.interfaces() if i.startswith('tun')]
        addrs = []
        for i in ifaces:
            addrs += netifaces.ifaddresses(i)[netifaces.AF_INET6]
        cjdaddrs = [i['addr'] for i in addrs if i['addr'].startswith('fc')]
        if cjdaddrs:
            return cjdaddrs[0]

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
