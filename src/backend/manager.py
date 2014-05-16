# -*- coding: utf-8 -*-

import netifaces
import threading

import gevent

from peer import Peer
from server import Server


class Manager(threading.Thread):
    'Manages everything in the backend'

    def __init__(self, friends, enemies, alias, status=1, statusmsg=''):
        super(Manager, self).__init__()

        self.friends = friends
        self.enemies = enemies

        self.address = self.get_address()
        self.server = Server(self)

        self.node = {}
        self.update_node(alias, status, statusmsg)

    def run(self):
        'Called when the thread is started'
        self.try_peers()
        self.server.start()
        gevent.wait()

    def get_address():
        'Returns the address that we care about, or None'
        ifaces = [i for i in netifaces.interfaces() if i.startswith('tun')]
        addrs = []
        for i in ifaces:
            addrs += netifaces.ifaddresses(i)[netifaces.AF_INET6]
        cjdaddrs = [i['addr'] for i in addrs if i['addr'].startswith('fc')]
        if cjdaddrs:
            return cjdaddrs[0]

    def update_node(self, alias=None, status=None, statusmsg=None):
        "Update this node's information"
        if alias is not None:
            self.node['alias'] = alias

        if status is not None:
            self.node['status'] = status

        if statusmsg is not None:
            self.node['status-message'] = statusmsg

    def try_peers(self):
        'Attempt to connect to all friends'
        self.peers = {}
        for addr, name in self.friends:
            self.peers[addr] = Peer.from_addr(self, addr, name)

    def new_connection(self, addr, sock):
        if addr in self.enemies:
            return

        elif addr in self.peers:
            self.peers[addr].recv_connect(sock)

        else:
            self.peers[addr] = Peer.from_socket(self, addr, sock)

    def update_information(self, **kwargs):
        for peer in self.peers.values():
            peer.send_packet(kwargs)
