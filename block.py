# BLOCK 
########################
##

import json

from time import time
from Crypto.Hash import SHA256

from transaction import Transaction

class Block:
    def __init__(self, previous_hash):
        """
        Initialize a block
        """
        self.previous_hash = previous_hash
        self.timestamp = time()
        self.hash = None
        self.nonce = None
        self.transactions_list = []
	
    def myHash(self):
        """
        Return hash of the block
        """
        block_info = [self.timestamp, [
            tr.transaction_id for tr in self.transactions_list],
            self.nonce, self.previous_hash]
        
        block_dump = json.dumps(block_info.__str__())

        self.hash = SHA256.new(block_dump.encode("ISO-8859-2")).hexdigest()
        return

    def add_transaction(transaction, blockchain):
        """
        Append a transaction to the current block
        """
        #add a transaction to the block
        return
    
    def validate_block(self):
        """
        Validate current_hash and previous_hash
        """
        return
		
    def mine_block():
        """
        Try to find a nonce once the block capacity has been reached
        """
        return

    def broadcat_block():
        """
        Broadcast the validated block once the nonce has been found
        """
        return

