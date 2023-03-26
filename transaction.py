# TRANSACTION 
########################
## 

import Crypto
import Crypto.Random

from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5

from blockchain import Blockchain

class Transaction:

    def __init__(self, sender_address, sender_private_key, receiver_address, value):
        """
        Initialize a new transaction (create_transaction)
        """
        self.sender_address = sender_address        # To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.receiver_address = receiver_address    # To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.amount = value                         # το ποσό που θα μεταφερθεί                    
        self.transaction_inputs = None              # λίστα από Transaction Input 
        self.transaction_outputs = None             # λίστα από Transaction Output 
        self.signature = None
        self.transaction_id = self.calculate_hash() # το hash του transaction

    def calculate_hash(self):
        """
        Calculate hash of transaction and use it as its ID
        """
        self.transaction_id = Crypto.Random.get_random_bytes(128).decode("ISO-8859-1")
        return

    def to_dict(self):
        """
        Convert transaction object to dictionary for readability.
        """
        dict = {
            "sender_address": self.sender_address,
            "receiver_address": self.receiver_address,
            "amount" : self.amount,
            "transaction_id" : self.transaction_id,
            "transaction_inputs" : self.transaction_inputs,
            "transaction_outputs" : self.transaction_outputs,
            "signature" : self.signature
        }
        return dict

    def sign_transaction(self, private_key):
        """
        Sign transaction with private key
        """
        # Pending: fix this !!
        # self.signature = PKCS1_v1_5.new(rsa_key=private_key).sign(self)
        return
    
    def verify_signature(self):
        """
        Verify signature of sender (private, public keys)
        """
        try:
            # Pending: fix this !!
            # PKCS1_v1_5.new(self.sender_address).verify(self.transaction_id, self.signature)
            return True
        except (ValueError, TypeError):
            return False

    def validate_transaction(self, id, UTXOs):
        """
        Verify signature of sender + 
        Verify sender has enough amount to spend
        """
        balance = 0
        for utxo in UTXOs[id]:
             balance += utxo.amount

             
        if (not self.verify_signature()):
            print("❌ Transaction NOT Validated : Not valid address")
            return False
        
        # elif(ring[str(self.sender_address)]['balance'] < self.amount ):
        #     print("❌ Transaction NOT Validated : Not enough coins")
        #     return False

        elif(balance < self.amount):
            print("❌ Transaction NOT Validated : Not enough coins")
            return False
        
        else: 
            print("✅ Transaction Validated !")
            return True