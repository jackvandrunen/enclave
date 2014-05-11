## **Enclave**

---

Enclave is a truly peer-to-peer instant messaging protocol. It entirely removes the idea of a server, as each node operates as both a client and a server simultaneously.

---

#### **Assumptions**

Enclave is not designed for use over just any network. It is designed for use over a network that utilizes the [cjdns](https://github.com/cjdelisle/cjdns) network suite. The two basic assumptions Enclave makes are as follows:

1. Each node has an address that is recognized globally across the network, with no concept of NATs or local network firewalls.

2. The address of every node is cryptographically derived, meaning that no two nodes can have the same address, a message sent from a particular node is guaranteed to be from that node, and the communication between two nodes is safe from eavesdropping.

---

#### **Network Protocol**

An Enclave node manages an "address book": a mapping of network addresses to human meaningful names, such as "John Smith." When an Enclave node is brought online, it tries to establish a connection with every node in its address book; the nodes that it is not able to connect to are considered "offline."

Internally, an Enclave client manages a TCP connection to every "friend" that it has, as well as a server listening on port 7776 for incoming connections. The TCP connection between two nodes is then used to relay messages back and forth.

When the server portion of a node receives a new connection, it should:

1. Check to see if the node on the other end is in the address book

2. If the node is not in the address book, then it should prompt the user to add it as a new contact

3. If the node is in the address book, then establish a connection

Data is sent between nodes over a TCP stream, which means that the data is not presented as individual packets to the applications. Thus, every Enclave "packet" takes the form of

    +------------------------+---------+
    | 4 byte length encoding | Content |
    +------------------------+---------+

The 4 byte length encoding is simply a 32 bit integer in network (big) endian format. For example, if the size of "content" was 256, the length encoding (represented here in hex) would be:

    00 00 01 00

---

#### **Protocol Specification**

The "content" portion of an Enclave "packet" is just a JSON string. Because JSON can be traditionally Unicode, it must be encoded as UTF-8 before being sent over the network.

These packets can have any number of different attributes. Some of the attributes are dependent on others, but some are independent.

NOTE: This is a constantly evolving spec, so expect changes.

---

`status` An integer sent to all peers when a node updates its status. It is up to the receiving node's front-end as to how this is displayed. The status codes are as follows:

0: Offline. It is good manners for a node that is shutting down to send out this status update. If a node receives an update from its peer with a status update to 0, it should close the connection.

1: Available. The human at the other end of the node is at the computer and is willing to chat.

2: Idle/Away. The human is not at the computer right now. An away status update should probably be accompanied by a `status-message` (described below) to indicate reasons and estimated time of return, but that is a human issue, not a protocol one.

3: Busy. The human does not wish to be disturbed and should not be expected to answer a message. A `status-message` should accompany this as well.

---

`status-message` A string sent to all peers when a node updates its status message. It is up to the receiving node's front-end as to how this is displayed.

---

`message` A string containing a message.

---

`timestamp` A UNIX timestamp formatted as an integer. Should be sent with every packet for reference, although it's up to the client to decide how to deal with it. Clients should also have the ability to deal with missing timestamp fields.

---

*Handshake*

When two clients connect, they both should send a single packet. This packet should contain the client's "status" and "status-message".

---