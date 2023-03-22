import argparse
from node import *
from wallet import *

# def test_method(receiver, amount):
#         print("all good" , receiver, amount)
def test_method2():
        print("method 2")
parser = argparse.ArgumentParser(description='Command Line Interface Noobcash')

subparsers = parser.add_subparsers(title='commands', dest='command')

#t <recipient_address> <amount>
#New transaction: Θα καλεί συνάρτηση create_transaction στο backend που θα
# υλοποιεί την παραπάνω λειτουργία
t_parser = subparsers.add_parser(name='t', help='Make a new transaction')
t_parser.add_argument('--recipient_address', required= True, help='Give recipient\'s IP address')
t_parser.add_argument('--amount', required= True, help='Give amount you would like to send')


#view
# View last transactions: Καλεί τη συνάρτηση view_transactions() στο backend που υλοποιεί την 
# παραπάνω λειτουργία
view_parser = subparsers.add_parser(name='view', help='View last transtactions')

# balance
# Show balance: Τύπωσε το υπόλοιπο του wallet.
balance_parser = subparsers.add_parser(name='balance', help='See wallet balance')

args = parser.parse_args()
if args.command == 't':
    Node.create_transaction(args.recipient_address, args.amount)
elif args.command == 'view':
        test_method2()
        # PENDING:  create view_transactions method in node.py
elif args.command == 'balance':
        Wallet.balance()
        # PENDING:  create view_transactions method in node.py
        
