# -*- coding: utf-8 -*-

'''The API for the Enclave backend.
Contains all the necessary functions for full interaction with the frontend.

NOTE: The frontend needs to handle saving and loading the friend and enemy
(ignore) list, as well as all the user's information.
'''

from manager import Manager


manager = None


get_address = Manager.get_address


def start(friends, enemies, alias, status, statusmsg):
    'Set up the manager and start the backend thread'
    global manager
    manager = Manager(friends, enemies, alias, statusmsg)
    manager.start()


def get_info(addr):
    'Get all information from a peer'
    node = manager.peers[addr]
    return {
        'alias': node.name,
        'status': node.status,
        'status-message': node.status_message,
        'log': node.log
    }


def update_info(alias=None, status=None, statusmsg=None):
    'Update global information (eg alias, status, status message)'
    info = {}
    if alias:
        info['alias'] = alias

    if status is not None:
        info['status'] = status

    if statusmsg is not None:
        info['statusmsg'] = statusmsg

    manager.update_node(**info)


def send_message(addr, message):
    'Send a message to a peer'
    node = manager.peers[addr]
    node.send_message(message)


def ignore(addr):
    'Ignore anything coming from a specific addr'
    manager.enemies.add(addr)
    node = manager.peers.get(addr)
    if node is not None:
        node.quit()
        del manager.peers[addr]
