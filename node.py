# NODE 
########################
## Responsible for creating and populating new blocks

# 1. Listens for new transactions
# 2a. Create a new Block if previous is full
# 2b. Begin mining if Block is full
# 3a. Stop mining if new Block get verified
# 3b. Begin mining of next block

# !! Each time you try to mine a block you create
# a temp version of all UTXOs. When a new block gets mined
# you discard the temp version and update the original UTXOs 
# database with the UTXOs derived from the mined block's transactions
# !! In case of conflict, get the UTXOs from the node with the longest chain

from wallet import Wallet
from blockchain import Blockchain
from transaction import Transaction

class Node:

    def __init__(self):
        self.wallet = Wallet() # create_wallet
        self.ip
        self.port
        self.name
        self.ring = []   # (id, address, pub_key, balance)
        self.blockchain = Blockchain()

    def create_transaction(self):
        our_address = self.wallet.public_key
        our_signature = self.wallet.private_key
        receipient = 'test'
        amount = 20
        transaction = Transaction(our_address, our_signature, receipient, amount)