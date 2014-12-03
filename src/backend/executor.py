"""
En taro Adun!
"""


def execute(self, directive):
    """Execute the directive that the frontend sent"""
    if directive['type'] == 'friend-response':
        if directive['accept']:
            self.friends.append(directive['addr'])
            self.peers[directive['addr']] = self.queued_connections[directive['addr']]
            del self.queued_connections[directive['addr']]

    if directive['type'] == 'quit':
        self.parent.quit()
