import threading
import socket
import netifaces


class Server(threading.Thread):

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

    def __init__(self, manager):
        super(Server, self).__init__()

        manager.address = self.get_address()
        self.manager = manager

        self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.server.bind((manager.address, 7776))

    def run(self):
        self.server.listen(5)

        while True:
            try:
                request, (addr, port) = self.server.accept()
                self.manager.new_connection(addr, request)

            except socket.error:
                break

    def stop(self):
        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()
