# -*- coding: utf-8 -*-

'''The API for the Enclave backend.
Contains all the necessary functions for full interaction with the frontend.

NOTE: The frontend needs to handle saving and loading the friend and enemy
(ignore) list, as well as all the user's information.
'''

import os
import json

from manager import Manager


manager = None


get_address = Manager.get_address


def load_config(path=None):
    'Load the configuration file to feed to the manager'
    if path is None:
        path = os.path.join(os.path.expanduser('~'), '.enclave')
        try:
            os.mkdir(path)
        except OSError:
            pass
        path = os.path.join(path, 'config.json')

    try:
        with open(path, 'r') as f:
            config = json.load(f)
        return config

    except Exception:
        config = {'friends': {}, 'enemies': [], 'alias': 'Anon',
                  'statusmsg': ''}
        save_config(config, path)
        return config


def save_config(config=None, path=None):
    if config is None:
        config = {'friends': manager.friends,
                  'enemies': list(manager.enemies),
                  'alias': manager.node['alias'],
                  'statusmsg': manager.node['status-message']}

    if path is None:
        path = os.path.join(os.path.expanduser('~'), '.enclave', 'config.json')

    with open(path, 'w') as f:
        json.dump(config, f)


def start():
    'Set up the manager and start the backend thread'
    global manager
    config = load_config()
    manager = Manager(**config)
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


def get_node():
    return manager.node


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


def add(addr, name):
    'Add a new friend based on cjdns address'
    manager.add_friend(addr, name)


def quit():
    manager.quit()
