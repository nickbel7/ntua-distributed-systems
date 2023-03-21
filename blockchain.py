# BLOCKCHAIN 
########################
## 

from dotenv import load_dotenv
import os

from block import Block

load_dotenv()
block_size = int(os.getenv('BLOCK_SIZE'))
mining_difficulty = int(os.getenv('MINING_DIFFICULTY'))

class Blockchain:
    def __init__(self):
        """
        Initialize a Blockchain
        """
        self.chain = [] # list<Block>
        self.difficulty = mining_difficulty
        self.maxBlockTransactions = block_size
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
