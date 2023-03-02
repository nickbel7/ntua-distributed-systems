# WALLET 
########################
## This is the implementation for a single wallet in the blockchain

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

class Wallet:

	def __init__(self):
		"""
	    Initialize a wallet
	    """
		# Reference: https://www.easydevguide.com/posts/python_rsa_keys
		key = RSA.generate(2048) # bits: 2048
		
		self.public_key = key
		self.private_key = key.publickey()
		self.address = key.publickey()
		# self.transactions

	def balance():
		"""
	    Get the total wallet balance
        """
		#...
		# Calculate the sum of all UTXOs