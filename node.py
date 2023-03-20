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

from collections import deque
from dotenv import load_dotenv
import requests
import pickle
import json
import os

from wallet import Wallet
from blockchain import Blockchain
from transaction import Transaction
from block import Block

load_dotenv()
block_size = int(os.getenv('BLOCK_SIZE'))

class Node:

    ################## CONSTRUCTOR ########################

    def __init__(self):
        """
        wallet:     Contains the wallet of each node
                    Also contains the private key, public key == address
        ip:         IP of the node
        port:       Port of the service the node listens to
        id:         A number that denotes the name of the node in the cluster
        ring:       A list of all the nodes in the cluster
        blockchain: A blockchain instance from the node's perspective
        nbc:        Amount of noobcoins the node has (for validation purposes)
        """
        self.wallet = Wallet() # create_wallet
        self.ip = None
        self.port = None
        self.id = None
        self.ring = []   # (id, address, pub_key, balance)
        self.blockchain = Blockchain()
        self.nbc = 0
        self.is_bootstrap = False
        self.current_block = None
        self.pending_blocks = deque()

    ##################### BLOCKS ###########################
    def create_new_block(self):
        """
        Creates a new block for the blockchain
        """
        previous_hash = None
        # Special case for GENESIS block
        if (len(self.blockchain.chain) == 0):
            previous_hash = 1
            
        self.current_block = Block(previous_hash)
        
        return self.current_block

    def add_transaction_to_block(self, transaction):
        """
        Add transaction to the block.

        If current block is None, then it creates one (the genesis block)
        """
        # Pending: Validate transaction

        # ==== UPDATING BLOCKCHAIN STATE ====
        # 1. If the transaction is related to node, update wallet
        if (transaction.receiver_address == self.wallet.address or 
            transaction.sender_address == self.wallet.address):
            self.wallet.transactions.append(transaction)
        #debug 
        print("Transaction appended to wallet")
        # print(self.wallet.transactions)
        
        # 2. Update the balance of sender and receiver in the ring.
        for node in self.ring:
            if node['address'] == transaction.sender_address:
                node['balance'] -= transaction.amount
            if node['address'] == transaction.receiver_address:
                node['balance'] += transaction.amount
        # debug
        print(self.ring)

        # ==== ADDING TRANSACTION TO BLOCK ====

        # Check if there is not an existing block create one
        if (self.check_full_block()):
            # Pending: begin the mining process
            previous_block = self.blockchain.chain[-1]
            previous_hash = previous_block.hash
            new_block = self.create_new_block()
            new_block.previous_hash = previous_hash
            self.current_block = new_block
            self.pending_blocks.appendleft(new_block)

        # Pending: Add transaction to the block
        self.current_block.transactions_list.append(transaction)

        return
    
    def check_full_block(self):
        if (len(self.current_block.transactions_list) == block_size):
            return True
        else:
            return False

    ################## TRANSACTIONS ########################

    def create_transaction(self, receiver, amount):
        our_address = self.wallet.address
        our_signature = self.wallet.private_key
        transaction = Transaction(our_address, our_signature, receiver, amount)
        
        # Sign the transaction.
        transaction.sign_transaction(our_signature)

        return transaction
    
    def unicast_transaction(self, node, transaction):
        request_address = 'http://' + node['ip'] + ':' + node['port']
        request_url = request_address + '/get_transaction'
        requests.post(request_url, pickle.dumps(transaction))
        
    def broadcast_transaction(self, transaction):
        for node in self.ring:
            if (self.id != node['id']):
                self.unicast_transaction(node, transaction)

    ################## BOOTSTRAPING ########################

    def add_node_to_ring(self, id, ip, port, address, balance):
        """
        ! BOOTSTRAP ONLY !
        Adds a new node to the cluster
        """
        self.ring.append(
            {
                'id': id,
                'ip': ip,
                'port': port,
                'address': address, # public key
                'balance': balance
            }
        )

    def unicast_node(self, node):
        """
        Sends information about self to the bootstrap node
        """
        request_address = 'http://' + node['ip'] + ':' + node['port']
        request_url = request_address + '/let_me_in'
        response = requests.post(request_url, data={
            'ip': self.ip,
            'port': self.port,
            'address': self.wallet.address
        })

        if response.status_code == 200:
            print("Node added successfully !")
            self.id = response.json()['id']
            print('My ID is: ', self.id)
        else:
            print("Initiallization failed")
    
    def unicast_ring(self, node):
        """
        ! BOOTSTRAP ONLY !
        Send the information about all the registered nodes 
        in the ring to a specific node
        """
        request_address = 'http://' + node['ip'] + ':' + node['port']
        request_url = request_address + '/get_ring'
        # requests.post(request_url, json=(self.ring)) # alternative
        requests.post(request_url, pickle.dumps(self.ring))

    def broadcast_ring(self):
        """
        ! BOOTSTRAP ONLY !
        Broadcast the information about the nodes to all nodes in the blockchain
        """
        for node in self.ring:
            if (self.id != node['id']):
                self.unicast_ring(node)

    def unicast_blockchain(self, node):
        """
        ! BOOTSTRAP ONLY !
        Send the information about the blockchain to a specified node
        """
        request_address = 'http://' + node['ip'] + ':' + node['port']
        request_url = request_address + '/get_blockchain'
        requests.post(request_url, pickle.dumps(self.blockchain))

    def broadcast_blockchain(self):
        """
        ! BOOTSTRAP ONLY !
        Broadcast the current state of the blockchain to all nodes
        """
        for node in self.ring:
            if (self.id != node['id']):
                self.unicast_blockchain(node)

    def unicast_initial_nbc(self, node):
        """
        ! BOOTSTRAP ONLY !
        Send the initial amount of 100 nbc to a specified node
        """
        # Create initial transaction (100 noobcoins)
        transaction = self.create_transaction(node['address'], 100)
        transaction.calculate_hash()

        # Broadcast transaction to other nodes in the network
        self.broadcast_transaction(transaction)
    
    def broadcast_initial_nbc(self):
        """
        ! BOOTSTRAP ONLY !
        Broadcast the initial amount of 100 nbc to each node
        """
        for node in self.ring:
            if (self.id != node['id']):
                self.unicast_initial_nbc(node)