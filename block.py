# BLOCK 
########################
##

from transaction import Transaction

class Block:
    def __init__(self):
        """
        Initialize a block
        """
        self.previous_hash
        self.timestamp
        self.hash
        self.nonce
        self.transactions_list = []
	
    def myHash(self):
        """
        Return hash of the block
        """
        #calculate self.hash

    def add_transaction(transaction, blockchain):
		"""
        Append a transaction to the current block
        """
        #add a transaction to the block
    
    def validate_block(self):
        """
        Validate current_hash and previous_hash
        """
		
    def mine_block():
        """
        Try to find a nonce once the block capacity has been reached
        """

    def broadcat_block():
        """
        Broadcast the validated block once the nonce has been found
        """

