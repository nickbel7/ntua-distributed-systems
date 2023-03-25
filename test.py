import time
import argparse
import requests
import socket
import random
import os
from dotenv import load_dotenv

from threading import Thread, Lock
from texttable import Texttable

################## ARGUMENTS #####################
argParser = argparse.ArgumentParser()
argParser.add_argument("-p", "--path", help="Destination of folder which contains transactions(id).txt", required=True)
args = argParser.parse_args()

path = args.path
load_dotenv()
CAPACITY = os.getenv('BLOCK_SIZE')
DIFFICULTY = os.getenv('MINING_DIFFICULTY')
NODES = os.getenv('TOTAL_NODES')

with open('./testing/results.txt', 'a') as f:
    f.write('CAPACITY:' + str(CAPACITY)+', DIFFICULTY:'+str(DIFFICULTY)+', NODES:'+str(NODES)+'\n')


nodes = []
with open("testing/nodes_addr.txt", 'r') as f:
    for line in f:
        nodes.append(line.strip('\n'))

def get_filename(id):
     return str(path)+"/transactions"+str(id)+".txt"

def send_transactions(file, addr):
    """
    This function reads from .txt files the transactions to be done.
    This is going to run in lot of threads at the same time, so to
    keep metrics (total_time, total_trans) safe we keep locks.
    """

    address= 'http://' + str(addr) + "/api/create_transaction/"

    counter = 0
    with open(file, 'r') as f:
        for line in f:
            time.sleep(random.uniform(0.1,0.5))
            #counter+=1
            #if(counter == 10):
            #    break
            line = line.split()
            receiver_id = int(line[0][2])
            amount = int(line[1])
            time.sleep(random.uniform(1,2))
            print(address+str(receiver_id)+'/'+str(amount))

            try:
                response = requests.get(address+str(receiver_id)+'/'+str(amount))
                data = response.json()
                print(data)

            except requests.exceptions.HTTPError:
                if (data):
                    print(data)

    return

# threads list
t_list = []

for id in range(len(nodes)):
    filename = get_filename(id)
    t_list.append(Thread(target= send_transactions, args=(filename, nodes[id])))

# Start the transactions
print("starting the transactions...")
for t in t_list:
     t.start()