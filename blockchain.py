# BLOCKCHAIN 
########################
## 

from dotenv import load_dotenv
import os

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
		
    def resolve_conflict(self):
        """
        Get the correct version of the blockchain when you cannot validate a block
        """
        for i in range(0, len(self.chain)-1):
            temp_block = self.chain[i]
            if (not (i==0 and temp_block.previous_hash == 1 and temp_block.nonce == 0)):
                    return False
            elif(not temp_block.validate_block(self)):
                 return False
            
        return True

    def wallet_balance(client_id, UTXOs):      
        """
	    Get the total wallet balance (based on the wallet of specific client_id)
		"""
        balance = 0
        for utxo in UTXOs[client_id]:
             balance += utxo.amount

        return balance