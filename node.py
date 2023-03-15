# NODE 
########################
## Responsible for creating and populating new blocks

# 1. Listens for new transactions
# 2a. Create a new Block if previous is full
# 2b. Begin mining if Block is full
# 3a. Stop mining if new Block get verified
# 3b. Begin mining of next block

# !! Each time you try to mine a block you create
# a temp version of all UTXOs. When a new block gets mined
# you discard the temp version and update the original UTXOs 
# database with the UTXOs derived from the mined block's transactions
# !! In case of conflict, get the UTXOs from the node with the longest chain

import requests
import pickle

from wallet import Wallet
from blockchain import Blockchain
from transaction import Transaction

class Node:

    ################## CONSTRUCTOR ########################

    def __init__(self):
        """
        wallet:     Contains the wallet of each node
                    Also contains the private key, public key == address
        ip:         IP of the node
        port:       Port of the service the node listens to
        name:       A number that denotes the name of the node in the cluster
        ring:       A list of all the nodes in the cluster
        blockchain: A blockchain instance from the node's perspective
        nbc:        Amount of noobcoins the node has (for validation purposes)
        """
        self.wallet = Wallet() # create_wallet
        self.ip
        self.port
        self.name
        self.ring = []   # (id, address, pub_key, balance)
        self.blockchain = Blockchain()
        self.nbc

    ################## TRANSACTIONS ########################

    def create_transaction(self, receiver, amount):
        our_address = self.wallet.public_key
        our_signature = self.wallet.private_key
        transaction = Transaction(our_address, our_signature, receiver, amount)

    ################## BOOTSTRAPING ########################

    def add_node_to_ring(self, ip, port, address, balance):
        """
        ! BOOTSTRAP ONLY !
        Adds a new node to the cluster
        """
        self.ring.append(
            {
                'ip': ip,
                'port': port,
                'address': address, # public key
                'balance': balance
            }
        )
    
    def unicast_ring(self, node):
        """
        ! BOOTSTRAP ONLY !
        Send the information about all the registered nodes 
        in the ring to a specific node
        """
        request_address = 'http://' + node['ip'] + ':' + node['port']
        request_url = request_address + '/get_ring'
        # Serialize the data before the request
        requests.post(request_url, data=pickle.dumps(self.ring))

    def broadcast_ring(self):
        """
        ! BOOTSTRAP ONLY !
        Broadcast the information about the nodes to all nodes in the blockchain
        """
        for node in self.ring:
            # missing : check if node is self
            self.unicast_ring(node)

    def unicast_blockchain(self, node):
        """
        ! BOOTSTRAP ONLY !
        Send the information about the blockchain to a specified node
        """
        request_address = 'http://' + node['ip'] + ':' + node['port']
        requeset_url = request_address + '/get_blockchain'
        # Serialize the data before the request
        requests.post(pickle.dumps(self.blockchain))

    def broadcast_blockchain(self):
        """
        ! BOOTSTRAP ONLY !
        Broadcast the current state of the blockchain to all nodes
        """
        for node in self.ring:
            # missing : check if node is self
            self.unicast_blockchain(node)