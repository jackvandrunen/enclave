import threading

import executor


Server = None
Peer = None


class Manager(threading.Thread):
    """Manages everything in the backend"""

    def __init__(self, parent, f2bq, b2fq, friends, enemies, alias, status=1, statusmsg='', protocol='cjdns'):
        super(Manager, self).__init__()

        self.parent = parent

        self.f2bq = f2bq  # For receiving
        self.b2fq = b2fq  # For sending

        self.friends = friends  # list of addresses
        self.enemies = enemies

        self.alias = alias
        self.status= status
        self.statusmsg = statusmsg

        self.choose_classes(protocol)

        self.peers = {}  # dict of {address: peer object}
        self.server = Server(self)

        self.queued_connections = {}  # {address: peer}

    @staticmethod
    def choose_classes(protocol):
        """Generates a server and peer class for the protocol desired"""
        if protocol == 'cjdns':
            global Server, Peer
            import servers.cjdns
            import peers.cjdns
            Server = servers.cjdns.Server
            Peer = peers.cjdns.Peer

    def run(self):
        """Called when the thread is started"""
        self.try_peers()
        self.server.start()

        while self.status:
            executor.execute(self, self.f2bq.get())  # Receive directives from the frontend

    def try_peers(self):
        """Try to connect to each peer, and populate the list of peers"""
        for addr in self.friends:
            if addr in self.peers and not self.peers[addr].status:
                self.peers[addr].try_connect()
            elif addr not in self.peers:
                self.peers[addr] = Peer.from_addr(self, addr)

    def new_connection(self, addr, stream):
        """A new inbound connection is passed in from the server"""
        if addr in self.friends:
            if addr in self.peers:
                self.peers[addr].recv_connect(stream)
            else:
                self.peers[addr] = Peer.from_socket(self, addr, stream)

        else:
            self.queued_connections[addr] = Peer.from_socket(self, addr, stream)
            self.send_to_frontend({
                'type': 'friend-request',
                'peer': self.queued_connections[addr]
            })

    def recv_message(self, addr, timestamp, alias, message):
        """Receive a message and pass it on to the frontend"""
        self.send_to_frontend({
            'type': 'message',
            'addr': addr,
            'timestamp': timestamp,
            'alias': alias,
            'message': message
        })

    def send_to_frontend(self, message):
        """Send a message (should be dict) to the frontend"""
        self.b2fq.put(message)

    def quit(self):
        """Exit the backend"""
        self.status = 0
        self.server.stop()
        for peer in self.peers.values():
            peer.quit()
