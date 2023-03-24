# BLOCKCHAIN 
########################
## 

from dotenv import load_dotenv
import requests
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
        for node in node.ring.values():
            if (node.id != node['id']):
                request_address = 'http://' + node['ip'] + ':' + node['port']
                # Comment: create endpoint (OK)
                request_url = request_address + '/get_chain_length'
                response_data = requests.get(request_url).json()
                len_value = response_data['chain_length']
                chain_lens.append(len_value)
            else: chain_lens.append(len(node.blockchain))
        
        # 3. find node wit longest chain
        max_len_index = chain_lens.index(max(chain_lens))
        if (max_len_index ==  node.id):
             return 
        else:
        # 4. send request to get the chain & utxos from the node
            request_url = request_address + '/get_blockchain'
            response_data = requests.get(request_url).json()
            response_chain = response_data['blockchain']
            node.blockchain = response_chain
            return

     # Comment: UTXOs is passed as parameter cause we might use temp_utxos
    def wallet_balance(client_id, UTXOs):      
        """
	    Get the total wallet balance (based on the wallet of specific client_id)
		"""
        balance = 0 
        
        for utxo in UTXOs[client_id]:
             balance += utxo.amount
        return balance