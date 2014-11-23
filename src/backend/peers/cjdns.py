import json
import socket
import threading
import time
import struct


class Peer(threading.Thread):
    """Manages a connection with another node"""

    @classmethod
    def from_socket(cls, master, addr, stream, log=[]):
        o = cls(master, addr)
        o.recv_connect(stream)
        return o

    @classmethod
    def from_addr(cls, master, addr, log=[]):
        o = cls(master, addr)
        o.try_connect()
        return o

    def __init__(self, master, addr, log=[]):
        super(Peer, self).__init__()

        self.master = master
        self.addr = addr
        self.alias = addr
        self.status = 0
        self.statusmsg = ''

        self.stream = None
        self.log = log
        self._buffer = ''

    def try_connect(self):
        """Try to establish a connection with another node"""
        try:
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            s.connect((self.addr, 7776))

            self.recv_connect(s)

        except socket.error:
            pass

    def recv_connect(self, stream):
        """A connection has been established"""
        if type(self.stream) is socket.socket:
            self.quit()

        self.stream = stream
        self.do_handshake()

        self.status = 1
        self.start()

    def do_handshake(self):
        """Sends a handshake packet"""
        data = {
            'alias': self.master.node['alias'],
            'status': self.master.node['status'],
            'statusmsg': self.master.node['statusmsg']
        }

        self.send_packet(data)

    def send_packet(self, data):
        """Pack and send a packet"""
        if type(self.stream) is not socket.socket:
            return False

        data['timestamp'] = int(time.time())

        packed = self.encode_length(json.dumps(data, separators=(',', ':')))

        self.stream.send(packed)

    def run(self):
        """The threaded part of the peer"""
        while self.status:
            try:
                packets = self.decode_length(self.stream.recv(4096))

            except socket.error:
                self.quit()
                break

            for raw in packets:
                try:
                    self.parse_packet(json.loads(raw))

                except ValueError:
                    continue

    def parse_packet(self, data):
        """Parse the JSON contents of a packet"""
        if data.get('timestamp') is None or type(data['timestamp']) is not int:
            data['timestamp'] = int(time.time())

        alias = data.get('alias')
        if alias is not None and not self.alias:
            self.alias = alias

        status = data.get('status')
        if status is not None and status == 0:
            self.quit()
        elif status and 0 < status < 4:
            self.status = status

        statusmsg = data.get('statusmsg')
        if statusmsg:
            self.statusmsg = statusmsg

        message = data.get('message')
        if message:
            self.log.append((data['timestamp'], self.alias, message))

    def encode_length(self, data):
        """Encode a 4 byte length prefix in network byte order"""
        length = struct.pack('!I', len(data))
        return '{0}{1}'.format(length, data)

    def decode_length(self, data):
        """Split a stream of received data into packets based on the length prefix"""
        packets = []
        data = '{0}{1}'.format(self._buffer, data)
        while data:
            try:
                length = struct.unpack('!I', data[:4])[0]
                packet = data[4:length + 4]
                if len(packet) != length:
                    self._buffer = data
                    break

                packets.append(packet)
                data = data[length + 4:]

            except struct.error:
                break

        return packets

    def quit(self):
        if type(self.stream) is socket.socket:
            self.status = 0
            try:
                self.stream.shutdown(socket.SHUT_RDWR)
            except socket.error:
                pass
            self.stream.close()
            self.join()
            self.stream = None

    def send_message(self, message):
        self.send_packet({'message': message})
        self.log.append((time.time(), self.master.node['alias'], message))
