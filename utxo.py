# UTXO (Unspent Transaction Output) 
########################
##

class UTXO:

    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def __json__(self):
            return {
                'sender': self.sender,
                'receiver': self.receiver,
                'amount': self.amount,
            }