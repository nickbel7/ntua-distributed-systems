# TRANSACTION 
########################
## 

from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5

class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value):
        """
        Initialize a new transaction (create_transaction)
        """
        self.sender_address = sender_address        # To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.receiver_address = recipient_address   # To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.amount = value                         # το ποσό που θα μεταφερθεί
        self.transaction_id                        # το hash του transaction
        self.transaction_inputs                     # λίστα από Transaction Input 
        self.transaction_outputs                    # λίστα από Transaction Output 
        self.signature = sender_private_key

    def calculate_hash(self):
        """
        Calculate hash of transaction and use it as its ID
        """
        self.transaction_id = SHA(self)

    def to_dict(self):
        """
        """

    def sign_transaction(self):
        """
        Sign transaction with private key
        """
        PKCS1_v1_5.new(rsa_key=self.signature).sign(self)
        

    def broadcast_transaction(self):
        """
        Send transaction to all nodes
        """
    
    def verify_signature(self):
        """
        Verify signature of sender (private, public keys)
        """

    def validate_transaction(self):
        """
        Verify signature of sender + 
        Verify sender has enough amount to spend
        """