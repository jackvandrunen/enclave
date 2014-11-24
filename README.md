## **Enclave**

---

Enclave is a truly peer-to-peer instant messaging protocol. It entirely removes the idea of a server, as each node operates as both a client and a server simultaneously. Enclave is primarily designed to be lightweight and efficient, unlike its (admittedly awesome) competitors like Tox, who carry a lot of overhead.

Enclave is not designed for use over just any network, however. It is designed primarily for use over a network that utilizes the [cjdns](https://github.com/cjdelisle/cjdns) network suite. The two basic assumptions Enclave makes are as follows:

1. Each node has an address that is recognized globally across the network, with no concept of NATs or local network firewalls.

2. The address of every node is cryptographically derived, meaning that no two nodes can have the same address, a message sent from a particular node is guaranteed to be from that node, and the communication between two nodes is safe from eavesdropping.

Other networking protocols and overlay protocols which have built in privacy and authentication mechanisms, and static addressing systems are suitable for use as well. People who are interested in writing the peer/server system for other protocols are welcome to contribute. Enclave is designed to be as network agnostic as possible.

---
