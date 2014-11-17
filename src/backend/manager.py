# -*- coding: utf-8 -*-

import netifaces
import threading

import gevent

from peer import Peer
from server import Server


class Manager(threading.Thread):
    'Manages everything in the backend'

    status_messages = {'available': 1, 'online': 1, 'idle': 2, 'away': 2,
                       'busy': 3}

    def __init__(self, friends, enemies, alias, status=1, statusmsg=''):
        super(Manager, self).__init__()

        self.friends = friends
        self.enemies = set(enemies)

        self.address = self.get_address()
        self.server = Server(self)

        self.node = {}
        self.peers = {}
        self.update_node(alias, status, statusmsg)

    def run(self):
        'Called when the thread is started'
        self.server.start()
        self.try_peers()
        gevent.wait()

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

    def update_node(self, alias=None, status=None, statusmsg=None):
        "Update this node's information"
        if alias is not None:
            self.node['alias'] = alias

        if status is not None:
            if type(status) is int:
                self.node['status'] = status

            else:
                try:
                    self.node['status'] = self.status_messages[status.lower()]
                except Exception:
                    pass

        if statusmsg is not None:
            self.node['status-message'] = statusmsg

        self.update_information(**self.node)

    def try_peers(self):
        'Attempt to connect to all friends'
        self.peers = {}
        for addr, name in self.friends.items():
            self.peers[addr] = Peer.from_addr(self, addr, name)

    def new_connection(self, addr, sock):
        print 'connection from %s' % addr
        if addr in self.enemies:
            return

        elif addr in self.peers:
            self.peers[addr].recv_connect(sock)

        else:
            self.peers[addr] = Peer.from_socket(self, addr, sock)

    def add_friend(self, addr, name):
        if addr in self.enemies:
            self.enemies.remove(addr)

        if addr not in self.friends:
            self.friends[addr] = name

            if addr not in self.peers:
                self.peers[addr] = Peer.from_addr(self, addr, name)

        return (name, self.peers[addr])

    def update_information(self, **kwargs):
        for peer in self.peers.values():
            peer.send_packet(kwargs)

    def quit(self):
        self.update_node(status=0)
