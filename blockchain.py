# TRANSACTION 
########################
## 

from block import Block

class Blockchain:
    def __init__(self):
        """
        Initialize a Blockchain
        """
        self.blockchain = [] # list<Block>
        self.difficulty
        self.maxBlockTransactions
        self.minimumTransaction
        self.UTXOs = []
        
    def validate_chain():
        """
        Validate the chain from the bootstrap node
        """
		
    def resolve_conflict():
        """
        Get the correct version of the blockchain when you cannot validate a block
        """
