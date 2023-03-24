# BLOCKCHAIN 
########################
## 

from dotenv import load_dotenv
import requests
import pickle
import os
import json
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
        # Comment: do we need this?
        # self.maxBlockTransactions = block_size    
        self.minimumTransaction = None
        self.UTXOs = []
    
    # def __json__(self):
    #     return {
    #         'chain': [block.__dict__ for block in self.chain],
    #         'difficulty': self.difficulty,
    #        # 'maxBlockTransactions': self.block_size,
    #         'minimumTransaction': self.minimumTransaction,
    #         'UTXOs': [list(i) for i in self.UTXOs ]
    #     }
    
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

    def resolve_conflict(node):
        """
        Get the correct version of the blockchain when you cannot validate a block
        """
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
        if (max_len_index ==  node.id):
             return 
        else:
        # 4. send request to get the chain & utxos from the node
            request_url = request_address + '/api/get_chain'
            response_data = requests.get(request_url)
            response_chain = pickle.loads(response_data.content)
        #     response_chain = json.loads(response_data)     
        #     new_chain = Blockchain()
        #     # # Comment: Debugging 
        #     # print("RESPONSE CHAIN: ", response_chain.keys())
        #     new_chain.chain = response_chain['chain']
        #     new_chain.difficulty = response_chain['difficulty']
        #    # new_chain.maxBlockTransactions = response_chain['maxBlockTransactions']
        #     new_chain.minimumTransaction = response_chain['minimumTransaction']
        #     new_chain.UTXOs = [deque(i) for i in response_chain['UTXOs']]
            
            node.blockchain = response_chain
            print("------------DEBUG NEW BLOCKCHAIN---------------", node.blockchain)
            return

     # Comment: UTXOs is passed as parameter cause we might use temp_utxos
    def wallet_balance(client_id, UTXOs):      
        """
	    Get the total wallet balance (based on the wallet of specific client_id)
		"""
        balance = 0 
        # DEBUG 
        print("DEBUG  ---------- ",client_id)
        for utxo in UTXOs[client_id]:
             balance += utxo.amount
        return balance
    
