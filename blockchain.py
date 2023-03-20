# TRANSACTION 
########################
## 

from block import Block

class Blockchain:
    def __init__(self):
        """
        Initialize a Blockchain
        """
        self.chain = [] # list<Block>
        self.difficulty = None
        self.maxBlockTransactions = None
        self.minimumTransaction = None
        self.UTXOs = []
        
    def validate_chain():
        """
        Validate the chain from the bootstrap node
        """
		
    def resolve_conflict():
        """
        Get the correct version of the blockchain when you cannot validate a block
        """
