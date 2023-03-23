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
import random
import threading

from wallet import Wallet
from blockchain import Blockchain
from transaction import Transaction
from block import Block

load_dotenv()
block_size = int(os.getenv('BLOCK_SIZE'))
mining_difficulty = int(os.getenv('MINING_DIFFICULTY'))

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
        is_bootstrap:   True if the current node is the Bootstrap node
        current_block:  The block that lefts to be filled with transactions
        pending_blocks: All the blocks that are filled with transactions but are not yet mined
        is_mining:      True if the node is in a state of mining the pending_blocks
        unmined_block:  True if the block that is currently being mined has not be mined by any other node 
        """
        self.wallet = Wallet() # create_wallet
        self.ip = None
        self.port = None
        self.id = None
        self.ring = {}     # address: (id, ip, port, balance) 
        self.blockchain = Blockchain()
        self.nbc = 0
        self.is_bootstrap = False
        self.current_block = None
        self.pending_blocks = deque()
        self.is_mining = False
        self.unmined_block = True


    ##################### MINING ###########################
    def create_new_block(self):
        """
        Creates a new block for the blockchain
        """
        previous_hash = None
        # Special case for GENESIS block
        if (len(self.blockchain.chain) == 0):
            previous_hash = 0
            
        self.current_block = Block(previous_hash)
        
        return self.current_block

    def add_transaction_to_block(self, transaction):
        """
        Add transaction to the block.

        If current block is None, then it creates one (the genesis block)
        """
        # Pending: Validate transaction

        print("========= NEW TRANSACTION 💵 ===========")

        # ==== UPDATING BLOCKCHAIN STATE ====
        # 1. If the transaction is related to node, update wallet
        if (transaction.receiver_address == self.wallet.address or 
            transaction.sender_address == self.wallet.address):
            self.wallet.transactions.append(transaction)
            #debug 
            print(f"1. Transaction appended to wallet. Got : {transaction.amount} NBCs")
        
        # 2. Update the balance of sender and receiver in the ring.
        self.ring[str(transaction.sender_address)]['balance'] -=  transaction.amount
        self.ring[str(transaction.receiver_address)]['balance'] +=  transaction.amount
        # debug
        print("2. Updated ring: ", self.ring.values())

        # ==== ADDING TRANSACTION TO BLOCK & MINING ====

        # Special case: after GENESIS block
        if self.current_block is None:
            self.current_block = self.create_new_block()

        # Add transaction to the block
        self.current_block.transactions_list.append(transaction)
        print("3. Current Block Transactions: ", [trans.amount for trans in self.current_block.transactions_list])
        print("4. Block size: ", len(self.current_block.transactions_list))
        # Check if block is full (in order to put it in the pending blocks)
        if (self.check_full_block()):
            # 1. Add block list of pending blocks to be mined
            self.pending_blocks.appendleft(self.current_block)
            # 2. Create a new block
            self.current_block = self.create_new_block()
            # 3. Trigger mining process
            # (!! put it in a seperate thread to avoid blocking other processes)
            mining_thread = threading.Thread(target=self.mine_process)
            mining_thread.start()

        return
    
    def check_full_block(self):
        """
        Checks if latest block in node is full
        """
        if (len(self.current_block.transactions_list) == block_size):
            return True
        else:
            return False

    def mine_process(self):
        if (self.pending_blocks and not self.is_mining):
            # Pending: should start a new thread
            print("========== BEGINING MINING ⛏️  ============")
            # 1. Initialize the mining
            self.is_mining = True
            while(self.pending_blocks):
                print("Number of pending blocks: ", len(self.pending_blocks))
                # 2. Get first block in list
                mined_block = self.pending_blocks.pop()
                # 3. Try to find the nonce
                is_mined_by_me = self.mine_block(mined_block)
                # 4. Broadcast it if you found it first
                if (is_mined_by_me):
                    print("Block was mined by: ", self.id)
                    self.broadcast_block(mined_block)
                    print("Block broadcasted successfully !")
                # 5. Reset the unmined_block flag
                self.unmined_block = True
            
            # Send the is_mining flag to false
            self.is_mining = False
            return

    def mine_block(self, block: Block):
        """
        Try to find a nonce once the block capacity has been reached
        """
         # 1. Initial nonce
        current_nonce = random.randint(0, 10000000)
        while(self.unmined_block):
            block.nonce = current_nonce
            current_hash = block.calculate_hash()
            # 2. Check if a correct nonce has been found
            if (current_hash.startswith('0' * mining_difficulty)):
                print('Hash found: ', current_hash[:10])
                result = True
                return result
            # 3. Try a different nonce
            # Try a .random() nonce each time (to avoid bias over the nodes)
            current_nonce = random.randint(0, 10000000)

        print("Block was ⛏️  by someone else 🧑")
        result = False
        return result

    def unicast_block(self, node, block):
        """
        Unicast the lastest mined block
        """
        request_address = 'http://' + node['ip'] + ':' + node['port']
        request_url = request_address + '/get_block'
        # requests.post(request_url, json=(self.ring)) # alternative
        requests.post(request_url, pickle.dumps(block))
    
    def broadcast_block(self, block: Block):
        """
        Broadcast the lastest mined block
        """
        for node in self.ring.values():
            if (self.id != node['id']):
                self.unicast_block(node, block)



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
        for node in self.ring.values():
            if (self.id != node['id']):
                self.unicast_transaction(node, transaction)



    ################## BOOTSTRAPING ########################

    def add_node_to_ring(self, id, ip, port, address, balance):
        """
        ! BOOTSTRAP ONLY !
        Adds a new node to the cluster
        """
        self.ring[str(address)] = {
                'id': id,
                'ip': ip,
                'port': port,
                'balance': balance
            }

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
        for node in self.ring.values():
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
        for node in self.ring.values():
            if (self.id != node['id']):
                self.unicast_blockchain(node)

    def unicast_initial_nbc(self, node):
        """
        ! BOOTSTRAP ONLY !
        Send the initial amount of 100 nbc to a specified node
        """
        # Create initial transaction (100 noobcoins)
        transaction = self.create_transaction(node, 100)
        transaction.calculate_hash()

        # Broadcast transaction to other nodes in the network
        self.broadcast_transaction(transaction)
    
    def broadcast_initial_nbc(self):
        """
        ! BOOTSTRAP ONLY !
        Broadcast the initial amount of 100 nbc to each node
        """
        for node_address in self.ring:
            if (self.id != self.ring[node_address]['id']):
                self.unicast_initial_nbc(node_address)