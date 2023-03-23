import inquirer
import os
import time
import argparse
import requests
import json

################## ARGUMENTS #####################
argParser = argparse.ArgumentParser()
argParser.add_argument("-p", "--port", help="Port in which node is running", default=8000, type=int)
argParser.add_argument("--ip", help="IP of the host")
args = argParser.parse_args()
# Address of node
ip_address = args.ip
port = args.port
address= 'http://' + str(ip_address) + ':' + str(port) + '/'

# Command Line Interface client
def client():
    os.system('cls||clear')
    while(True):

        menu = [ 
            inquirer.List('menu', 
            message= "Noobcash Client", 
            choices= ['💸 New transaction', '📭 View last transactions', '💰 Show balance', '🌙 Exit'], 
            ),
        ]
        choice = inquirer.prompt(menu)['menu']
        os.system('cls||clear')

        if choice == '💸 New transaction':
            questions = [
                inquirer.Text(name='recipent', message ='🍀 What is the Recipent ID of the lucky one?'),
                inquirer.Text(name='amount', message = '🪙 How many noobcoins to send?'),
            ]
            answers = inquirer.prompt(questions)
            recipent = str(answers['recipent'])
            amount = str(answers['amount'])
                           
            print('Sending ' + amount + ' NoobCoins to client with ID ' + str(answers['recipent']) + '...')
            time.sleep(2)

            try:
                response = requests.get(address+'/api/create_transaction/'+recipent+'/'+amount)
                print(json.loads(response))

            except:
                print("Node is not available or active. Try again later.")
                time.sleep(2)
                
            os.system('cls||clear')
            continue
        
        if choice == '📭 View last transactions':
            # call api
            # print results
            continue
        
        if choice == '💰 Show balance':
            # call api
            # print results
            continue
        
        if choice == '🌙 Exit':
            os.system('cls||clear')
            print("We will miss you 💋")
            time.sleep(0.7)
            os.system('cls||clear')
            break

client()