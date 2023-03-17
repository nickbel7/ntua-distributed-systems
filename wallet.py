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
	    Initialize a wallet (generate_wallet)
	    """
		# Reference: https://www.easydevguide.com/posts/python_rsa_keys
		key = RSA.generate(2048) # bits: 2048
		
		self.private_key = key
		self.public_key = key.publickey()
		self.address = key.publickey().exportKey().decode('ISO-8859-1')
		# self.transactions

	def balance():
		"""
	    Get the total wallet balance
		"""
		#...
		# Calculate the sum of all UTXOs

# Testing
# new_wallet = Wallet()
# print(new_wallet.private_key.export_key().decode())