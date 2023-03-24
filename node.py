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
from copy import deepcopy
from dotenv import load_dotenv
import requests
import pickle
import json
import os
import random
import threading
import time

from wallet import Wallet
from blockchain import Blockchain
from transaction import Transaction
from block import Block
from utxo import UTXO

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
        self.ring = {}     # address: {id, ip, port, balance} 
        self.blockchain = Blockchain()
        self.is_bootstrap = False
        self.current_block = None
        # self.pending_blocks = deque()
        self.is_mining = False
        self.incoming_block = False
        self.pending_transactions = deque()
        self.temp_utxos = None  # for validation purposes


    ##################### MINING ###########################
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

    def add_transaction_to_pending(self, transaction: Transaction):
        """
        """
        # 1. Add transaction to pending list
        self.pending_transactions.appendleft(transaction)

        # Special case: after GENESIS block
        if self.current_block is None:
            self.current_block = self.create_new_block()

        # 2. Begin mining process if node is idle
        if (not self.is_mining):
            mining_thread = threading.Thread(target=self.mine_process)
            mining_thread.start()

        return


    def update_wallet_state(self, transaction: Transaction):
        """
        """
        # 1. If the transaction is related to node, update wallet
        if (transaction.receiver_address == self.wallet.address or 
            transaction.sender_address == self.wallet.address):
            self.wallet.transactions.append(transaction)
            #debug 
            print(f"1. Transaction appended to wallet. {self.ring[transaction.sender_address]['id']} -> {self.ring[transaction.receiver_address]['id']} : {transaction.amount} NBCs")
        
        # 2. Update the balance of sender and receiver in the ring.
        self.ring[str(transaction.sender_address)]['balance'] -=  transaction.amount
        self.ring[str(transaction.receiver_address)]['balance'] +=  transaction.amount
        # debug
        print("2. Updated ring: ", self.ring.values())
        return

    def add_transaction_to_block(self, transaction: Transaction):
        """
        Add transaction to the block.

        If current block is None, then it creates one (the genesis block)
        """

        print("========= NEW TRANSACTION 💵 ===========")

        # Validate transaction
        if ((transaction.sender_address != self.wallet.address) 
            and (not transaction.validate_transaction(self.ring))):
            print("Transaction not valid :(")

        # ==== UPDATING BLOCKCHAIN STATE ====
        # 1. If the transaction is related to node, update wallet
        if (transaction.receiver_address == self.wallet.address or 
            transaction.sender_address == self.wallet.address):
            self.wallet.transactions.append(transaction)
            #debug 
            print(f"1. Transaction appended to wallet. {self.ring[transaction.sender_address]['id']} -> {self.ring[transaction.receiver_address]['id']} : {transaction.amount} NBCs")
        
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
    
    def update_original_utxos(self, transaction: Transaction):
        sender_address = transaction.sender_address
        receiver_address = transaction.receiver_address
        amount = transaction.amount
        sender_id = self.ring[str(sender_address)]['id']
        receiver_id = self.ring[str(receiver_address)]['id']
        self.blockchain.UTXOs[receiver_id].append(UTXO(sender_id, receiver_id, amount))
        total_amount = 0
        while(total_amount < amount):
            temp_utxo = self.blockchain.UTXOs[sender_id].popleft()
            total_amount += temp_utxo.amount
        if (total_amount > amount):
            self.blockchain.UTXOs[sender_id].append(UTXO(sender_id, sender_id, total_amount-amount))

        return
    
    def update_temp_utxos(self, transaction: Transaction):
        # UTXO attributes
        sender_address = transaction.sender_address
        receiver_address = transaction.receiver_address
        amount = transaction.amount
        sender_id = self.ring[str(sender_address)]['id']
        receiver_id = self.ring[str(receiver_address)]['id']
        # Update receiver UTXOs
        self.temp_utxos[receiver_id].append(UTXO(sender_id, receiver_id, amount))
        # Update sender UTXOs
        total_amount = 0
        while(total_amount < amount):
            temp_utxo = self.temp_utxos[sender_id].popleft()
            total_amount += temp_utxo.amount
        if (total_amount > amount):
            self.temp_utxos[sender_id].append(UTXO(sender_id, sender_id, total_amount-amount))

        return

    # DEPRECATED
    # def check_pending_transactions(self):
        # while(True):
        #     if (self.pending_transactions and not self.is_mining and not self.incoming_block):
        #         # Add transaction to the block
        #         transaction = self.pending_transactions.pop()
        #         if (transaction.validate_transaction(self.blockchain.UTXOs)):
        #             self.current_block.transactions_list.append(transaction)
        #             self.update_temp_utxos(transaction)
        #             # Check if block is full
        #             if (self.check_full_block()):
        #                 mining_thread = threading.Thread(target=self.mine_process)
        #                 mining_thread.start()
        # return
    
    def check_full_block(self):
        """
        Checks if latest block in node is full
        """
        if (len(self.current_block.transactions_list) == block_size):
            return True
        else:
            return False

    def mine_process(self):
        # if (self.pending_blocks and not self.is_mining):
        # Pending: should start a new thread
        # 1. Initialize the mining
        self.is_mining = True
        # while(self.pending_blocks):
        # print("Number of pending blocks: ", len(self.pending_blocks))
        # 2. Get first block in list
        # mined_block = self.pending_blocks.pop()
        # 3. Try to find the nonce
        while (self.pending_transactions):
            transaction = self.pending_transactions.pop()
            if (transaction.validate_transaction(self.temp_utxos)):
                # Add transaction to the block
                self.current_block.transactions_list.append(transaction)
                self.update_temp_utxos(transaction)
                if (self.check_full_block()):
                    print("========== BEGINING MINING ⛏️  ============")
                    # 1. Mine current_block
                    is_mined_by_me = self.mine_block(self.current_block)
                    # 4. Broadcast it if you found it first
                    if (is_mined_by_me):
                        print("Block was mined by: ", self.id)
                        # Add block to originanl chain (assuming it has been validated)
                        self.blockchain.chain.append(self.current_block)
                        for transaction in self.current_block.transactions_list:
                            self.update_wallet_state(transaction)
                            self.blockchain.UTXOs = self.temp_utxos

                        self.broadcast_block(self.current_block)

                        print("Block broadcasted successfully !")
                    else:
                        # Synchronize blockchain
                        # time.sleep(1)
                        while(self.incoming_block):
                            # time.sleep()
                            continue
                        # 5. Reset the incoming_block flag
                        # self.incoming_block = False
                        
                    # Create a new block
                    self.current_block = self.create_new_block()        
                
        # Send the is_mining flag to false
        self.is_mining = False
        return

    def update_pending_transactions(self, incoming_block: Block):
        # 1. Add transactions of current_block to pending_transactions list
        for transaction in self.current_block.transactions_list:
            self.pending_transactions.append(transaction)
        # 2. Remove from pending_transactions all transactions included in the incoming_block
        for incoming_transaction in incoming_block.transactions_list:
            index = 0
            while index < len(self.pending_transactions):
                pending_transaction = self.pending_transactions[index]
                if (pending_transaction.transaction_id == incoming_transaction.transaction_id):
                    self.pending_transactions.remove(pending_transaction)
                else:
                    index += 1

        return

    def add_block_to_chain(self, block: Block):
        # Add block to originanl chain (assuming it has been validated)
        self.blockchain.chain.append(block)
        # Update UTXOs and wallet accordingly
        for transaction in block.transactions_list:
            self.update_original_utxos(transaction)
            self.update_wallet_state(transaction)
        # Reset temp_utxos
        self.temp_utxos = deepcopy(self.blockchain.UTXOs)
        # Update pending_transactions list
        self.update_pending_transactions(block)

        # Update incoming_block flag
        self.incoming_block = False
        # mined: [1, 2, 4]
        # current: [2, 3]
        # pending: [2, 3, 1, 4]

    def mine_block(self, block: Block):
        """
        Try to find a nonce once the block capacity has been reached
        """
         # 1. Initial nonce
        current_nonce = random.randint(0, 10000000)
        while(not self.incoming_block):
            block.nonce = current_nonce
            current_hash = block.calculate_hash()
            # 2. Check if a correct nonce has been found
            if (current_hash.startswith('0' * mining_difficulty)):
                print('Hash found: ', current_hash[:10])
                return True
            # 3. Try a different nonce
            # Try a .random() nonce each time (to avoid bias over the nodes)
            current_nonce = random.randint(0, 10000000)

        print("Block was ⛏️  by someone else 🧑")
        return False

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

        # Calculate the hash
        transaction.calculate_hash()

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
        
        # Create UTXOs for new node
        self.blockchain.UTXOs.append(deque())

        return

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

        return
    
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
        # Create a copy of original UTXOs
        self.temp_utxos = deepcopy(self.blockchain.UTXOs)
        
        for node in self.ring.values():
            if (self.id != node['id']):
                self.unicast_blockchain(node)

    def unicast_initial_nbc(self, node_address):
        """
        ! BOOTSTRAP ONLY !
        Send the initial amount of 100 nbc to a specified node
        """
        # Create initial transaction (100 noobcoins)
        transaction = self.create_transaction(node_address, 100)

        # Add transaction to block
        # self.add_transaction_to_block(transaction)
        self.add_transaction_to_pending(transaction)

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