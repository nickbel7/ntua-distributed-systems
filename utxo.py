# UTXO (Unspent Transaction Output) 
########################
##

class UTXO:

    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
