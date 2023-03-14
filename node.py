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

    def __init__(self):
        self.wallet = Wallet() # create_wallet
        self.ip
        self.port
        self.name
        self.ring = []   # (id, address, pub_key, balance)
        self.blockchain = Blockchain()
        self.nbc

    def create_transaction(self):
        our_address = self.wallet.public_key
        our_signature = self.wallet.private_key
        receipient = 'test'
        amount = 20
        transaction = Transaction(our_address, our_signature, receipient, amount)

    def add_node_to_ring(self, ip, port, address, balance):
        self.ring.append(
            {
                'ip': ip,
                'port': port,
                'address': address,
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
            self.unicast_blockchain(node)