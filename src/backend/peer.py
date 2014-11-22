# -*- coding: utf-8 -*-

import socket
import json
import time
import struct
import threading


class Peer(threading.Thread):
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
        super(Peer, self).__init__()
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
        print 'recv_connect called'
        if self.stream is not None:
            self.quit()
        print 'working...'

        self.stream = stream
        self.do_handshake()
        print 'still working...'

        self.status = 1
        self.start()
        print 'yup'

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
        print 'sent: %s' % packed

    def run(self):
        'Receive packets, parse them, and send them off for interpretation'
        print 'recv_packet called'
        while self.status:
            try:
                print 'waiting to receive packets!'
                packets = self.decode_length(self.stream.recv(4096))
                print 'received: %s' % repr(packets)
            except Exception, e:
                print e
                packets = []

            if not packets:
                print 'NO PACKETS!'
                self.quit()
                return

            print 'received valid packets!'

            for raw in packets:
                try:
                    data = json.loads(raw)
                    print 'received: %s' % str(data)
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
        print 'quit called!'
        if self.stream:
            self.status = 0
            self.stream.shutdown(socket.SHUT_RDWR)
            self.stream.close()
            self.worker.join()
            self.stream = None

    def send_message(self, message):
        self.send_packet({'message': message})
        self.log.append((time.time(), self.master.node['alias'], message))
