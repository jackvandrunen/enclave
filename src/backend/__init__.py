"""
Enclave is frontend agnostic. The frontend and backend communicate via two FIFO queues.
"""


import Queue

from manager import Manager


# Frontend to backend communication (sending messages, adding friends, updating status, etc)
f2bq = Queue.Queue()

# Backend to frontend communication (receiving messages, connections from friends, friend status, etc)
b2fq = Queue.Queue()


master = None


def start(friends, enemies, alias, status=1, statusmsg='', protocol='cjdns'):
    """Start the backend"""
    global master
    master = Manager(f2bq, b2fq, friends, enemies, alias, status, statusmsg, protocol)
    master.start()
    return f2bq, b2fq
