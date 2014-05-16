# -*- coding: utf-8 -*-

from gevent import socket, spawn

import json
import time
import struct


class Peer(object):
    'Manages a connection with another friendly node'

    @classmethod
    def from_socket(cls, master, addr, sock):
        o = cls(master, addr)
        o.recv_connect(sock)
        return o

    @classmethod
    def from_addr(cls, master, addr, name):
        o = cls(master, addr, name)
        o.try_connect()
        return o

    def __init__(self, master, addr, name=''):
        self.master = master
        self.name = name
        self.addr = addr
        self.status = 0
        self.status_message = ''
        self.stream = None
        self.log = []
        self._buffer = ''
        self.worker = None

    def try_connect(self):
        'Try to establish a connection with the other node'
        try:
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            s.connect((self.addr, 7776))

            self.recv_connect(s)

        except socket.error:
            pass

    def recv_connect(self, stream):
        'A connection has been established'
        if self.stream is not None:
            self.quit()

        self.stream = stream
        self.do_handshake()

        self.status = 1
        self.worker = spawn(self.recv_packet)

    def do_handshake(self):
        'Sends a handshake packet'
        data = {
            'alias': self.master.node['alias'],
            'status': self.master.node['status'],
            'status-message': self.master.node['status-message']
        }

        self.send_packet(data)

    def send_packet(self, data):
        'Pack and send a packet'
        if self.stream is None:
            return False

        data['timestamp'] = int(time.time())

        packed = self.encode_length(json.dumps(data, separators=(',', ':')))

        self.stream.send(packed)

    def recv_packet(self):
        'Receive packets, parse them, and send them off for interpretation'
        while self.status:
            try:
                packets = self.decode_length(self.socket.recv(4096))
            except Exception:
                packets = []

            if not packets:
                self.quit()
                return

            for raw in packets:
                try:
                    data = json.loads(raw)
                    self.parse_packet(data)

                except Exception:
                    continue

    def parse_packet(self, data):
        'Parse the contents of a packet'
        if not data.get('timestamp'):
            data['timestamp'] = int(time.time())

        alias = data.get('alias')
        if alias is not None and not self.name:
            self.name = alias

        status = data.get('status')
        if status is not None and status == 0:
            self.quit()
        elif status and 0 < status < 4:
            self.status = status

        status_message = data.get('status-message')
        if status_message:
            self.status_message = status_message

        message = data.get('message')
        if message:
            self.log.append((data['timestamp'], self.name, message))

    def encode_length(self, data):
        'Encode a 4 byte length prefix'
        length = struct.pack('!I', len(data))
        return '{0}{1}'.format(length, data)

    def decode_length(self, data):
        'Split a chunk of received data into packets based on the 4 byte prefix'
        packets = []
        data = '{0}{1}'.format(self._buffer, data)
        while data:
            try:
                length = struct.unpack('!I', data[:4])[0]
                packets.append(data[4:length + 4])
                data = data[:length + 4]

            except Exception:
                self._buffer = data

        return packets

    def quit(self):
        'Goodbye for now!'
        if self.stream:
            self.status = 0
            self.stream.shutdown(socket.SHUT_RDWR)
            self.stream.close()
            self.worker.join()
            self.stream = None

    def send_message(self, message):
        self.send_packet({'message': message})
        self.log.append((time.time(), self.master.node['alias'], message))
