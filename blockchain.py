# BLOCKCHAIN 
########################
## 

from dotenv import load_dotenv
import requests
import pickle
import os
from collections import deque

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
        self.trxns = set()
        
    def validate_chain(self):
        """
        Validate the chain from the bootstrap node
        """
        for i in range(0, len(self.chain)-1):
            temp_block = self.chain[i]
            if (not (i==0 and temp_block.previous_hash == 1 and temp_block.nonce == 0)):
                    return False
            elif(not temp_block.validate_block(self)):
                 return False
        return True
    
    def resolve_conflict(self, node):
        """
        Get the correct version of the blockchain when you cannot validate a block
        """
        print("☠️  FOUND CONFLICT: Initializing Resolve Conflict Method")
        # 1. initialize list to hold the len of the chains 
        chain_lens = []
        # 2. Send request to all nodes to send back the current len of the blockchain 
        for n in node.ring.values():
            if (node.id != n['id']):
                request_address = 'http://' + n['ip'] + ':' + n['port']
                # Comment: create endpoint (OK)
                request_url = request_address + '/api/get_chain_length'
                response_data = requests.get(request_url).json()
                # Comment: debug
                print("DEBUGGING: ", response_data)
                len_value = response_data['chain_length']
                chain_lens.append(len_value)
            else: chain_lens.append(len(node.blockchain.chain))
        
        # 3. find node wit longest chain
        max_len_index = chain_lens.index(max(chain_lens))
        print("🫥 YOUR CHOICES WERE", chain_lens)
        print("👌 FOUND LONGEST CHAIN: Node, ", max_len_index)
        if (max_len_index ==  node.id):
             print("😁 LONGEST CHAIN WAS MINE")
             return 
        else:
            # 4. send request to get the chain & utxos from the node
            request_url = request_address + '/api/get_chain'
            response_data = requests.get(request_url)
            response_chain = pickle.loads(response_data.content)
            print("😒 HAD TO CHANGE CHAIN")
            node.blockchain = response_chain
            return

    def wallet_balance(client_id, UTXOs):      
        """
	    Get the total wallet balance (based on the wallet of specific client_id)
		"""
        balance = 0
        for utxo in UTXOs[client_id]:
             balance += utxo.amount

        return balance