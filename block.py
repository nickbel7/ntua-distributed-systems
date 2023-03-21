# BLOCK 
########################
##
from hashlib import sha256
from time import time
import json
import requests
# from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
from transaction import Transaction

class Block:
    def __init__(self, previous_hash, capacity):
        """
        Initialize a block
        """
        self.previous_hash = previous_hash
        self.timestamp = time()
        self.hash = None
        self.nonce = None
        self.transactions_list = []
        self.capacity = capacity 
	
    def myHash(self):
        """
        Return hash of the block
        """
        #calculate self.hash
        json_object = {'nonce': self.nonce, 'previous hash': self.previous_hash, 'timestamp': self.timestamp, 'transactions': self.transactions_list}
        json_data = json.dumps(json_object)
        hash_object = sha256.new()
        hash_object.update(json_data.encode())    
        hash_digest = hash_object.digest()
        
        return hash_digest

    
    def validate_block(self, blockchain):
        """
        Validate current_hash and previous_hash
        Called from a node when it receives a broadcasted block (that isn't the genesis block)
        Checks 1)if current_hash is correct
               2)if the previous_hash field is equal to the the hash of the actual previous block
        """
        
        #if it is the genesis block, it's valid 
        if (self.previous_hash == 0 & self.nonce == 0):
            return True
        #else get last valid block of blockchain and check 
        prev_block = blockchain.blockchain[-1:]
        if ( (prev_block.previous_hash == self.previous_hash) 
            & (prev_block.hash =="0" * blockchain.difficulty) ):
            return True
        return False

   # PENDING: πότε καλείται? Θα πρέπει το node να κάνει συνέχεια mine, όσο έχει blocks στο blocks_to_mine
   # PENDING: σταματάει το mining του τρέχοντος block αν φτάσει mined από άλλο node στο ring
    def mine_block(self,node, difficulty):
        """
        Try to find a nonce once the block capacity has been reached
        """
        while(node.blocks_to_mine.len() != 0):
            block = node.blocks_to_mine.popleft()
            nonce = 0
            while True:
                block.nonce = nonce
                hash_value = block.myHash()

                # Check if the hash meets the difficulty level requirement
                if hash_value[:difficulty] == "0" * difficulty:
                    # Valid hash found, exit the loop]
                    block.hash = hash_value
                    block.broadcast_block()
                    break

                # Else, increment the nonce and try again
                nonce += 1

        return

    def broadcast_block(self,node_self):
        """
        Broadcast the validated block once the nonce has been found
        """
        for node in node_self.ring:
            if (node_self.id != node['id']):
                request_address = 'http://' + node['ip'] + ':' + node['port']
                request_url = request_address + '/get_mined_block'     #FIX METHOD
                requests.post(request_url, json=(self))
        return

    def add_transaction(self,transaction,node, blockchain):
        """
        Append a transaction to the current block
        """
        self.transactions_list.append(transaction)
        if len(self.transactions_list) == self.capacity:
               # self.mine_block()   
            node.blocks_to_mine.append(self)
        return
