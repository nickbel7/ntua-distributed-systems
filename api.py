from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import socket
import json
import uvicorn
import argparse
import pickle
import time
import threading
import requests

from node import Node
from transaction import Transaction

app = FastAPI()
# app = APIRouter()

# CORS (Cross-Origin Resource Sharing)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

################## ARGUMENTS #####################
argParser = argparse.ArgumentParser()
argParser.add_argument("-p", "--port", help="Port in which node is running", default=8000, type=int)
argParser.add_argument("--ip", help="IP of the host")
args = argParser.parse_args()

################## HELPER FUNCTIONS #####################
def create_genesis_block():
    """
    ! BOOTSTRAP ONLY !
    Create the first block of the blockchain (GENESIS BLOCK)
    """
    # 1. Create new block
    gen_block = node.create_new_block() # previous_hash autogenerates
    gen_block.nonce = 0

    # 2. Create first transaction
    first_transaction = Transaction(
        sender_address='0', 
        sender_private_key=None, 
        receiver_address = node.wallet.address, 
        value = total_nbc
    )

    # 3. Add transaction to genesis block
    gen_block.transactions_list.append(first_transaction)
    gen_block.calculate_hash() # void

    # 4. Add genesis block to bockchain
    node.blockchain.chain.append(gen_block)
    
    return

################## INITIALIZATION #####################
# Step 1. 
# Initialize the new node
node = Node()

# Step 2.
# Get info about the cluster, bootstrap node
load_dotenv()
total_nodes = int(os.getenv('TOTAL_NODES'))
total_nbc = total_nodes * 100

bootstrap_node = {
    'ip': os.getenv('BOOTSTRAP_IP'),
    'port': os.getenv('BOOTSTRAP_PORT')
}

# Step 3.
# Set the IP and PORT
# DOCKER SPECIFIC
# ip_address = socket.gethostbyname('host.docker.internal')
ip_address = args.ip
# IP ADDRESS
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.connect(("8.8.8.8", 80))
# ip_address = s.getsockname()[0]
print('IP address: ', ip_address) # debug
# s.close()
# PORT
port = args.port
print('PORT: ', port) # debug
node.ip = ip_address
node.port = str(port)

# Step 4. 
# See if node is Bootstrap node
if (ip_address == bootstrap_node["ip"] and str(port) == bootstrap_node["port"]):
    node.is_bootstrap = True
    print("I am bootstrap")

# Step 5.
# Register node to the cluster
if (node.is_bootstrap):
    # Add himself to ring
    node.id = 0
    node.add_node_to_ring(node.id, node.ip, node.port, node.wallet.address, total_nbc)
    create_genesis_block()

else:
    node.unicast_node(bootstrap_node)

################## ROUTES #####################
@app.get("/")
async def root():
    # return {"message": f"Welcome to Noobcoin. I am {socket.gethostname()} : {socket.gethostbyname(socket.gethostname())}"}
    return {"message": f"Welcome to Noobcoin"}

@app.post("/get_ring")
async def get_ring(request: Request):
    """
    Gets the completed list of nodes from Bootstrap node
    """
    data = await request.body()
    node.ring = pickle.loads(data)

    print("Ring received successfully !")

@app.post("/get_blockchain")
async def get_blockchain(request: Request):
    """
    Gets the lastest version of the blockchain from the Bootstrap node
    """
    data = await request.body()
    node.blockchain = pickle.loads(data)

    print("Blockchain received successfully !")

@app.post("/get_transaction")
async def get_transaction(request: Request):
    """
    Gets an incoming transaction and adds it in the block.
    """
    data = await request.body()
    new_transaction = pickle.loads(data)
    print("---> New transaction received")

    # Add transaction to block
    node.add_transaction_to_block(new_transaction)

@app.post("/get_block")
async def get_block(request: Request):
    """
    Gets an incoming mined block and adds it to the blockchain.
    """
    data = await request.body()
    new_block = pickle.loads(data)
    print("New block received successfully !")

    # Pending: implement logic when receiving a block
    # 1. Check validity of block
    previous_hash = node.blockchain.chain[-1].hash
    new_block.previous_hash = previous_hash 
    if (new_block.validate_block(node.blockchain)):
        # If it is valid:
        # 1. Stop the current block mining
        node.unmined_block = False
        # 2. Add block to the blockchain
        node.blockchain.chain.append(new_block)
        print("✅📦! \nAdding it to the chain")
        print("Blockchain length: ", len(node.blockchain.chain))
    else:
        print("❌📦 Something went wrong with validation :(")

    return JSONResponse('OK')

@app.post("/create_transaction")
async def create_transaction():
    """
    Creates a new transaction given a receiver wallet and an amount
    """
    # 1. Create transaction
    # 2. Calculate hash
    # 3. Add to block
    # 4. Broadcast transaction

@app.get("/view_transactions")
async def view_transactions():
    """
    Returns the transactions of the last validated, mined block
    """
    # 1. Get last block in the chain
    # 2. Return a list of transactions (sender, receiver, amount)

@app.get("/get_balance")
async def get_balance():
    """
    Gets the total balance for the given node (in NBCs)
    """
    # 1. Get the NBCs attribute from the node object

@app.post("/let_me_in")
async def let_me_in(request: Request):
    #https://i.imgflip.com/2u5y6a.png?a466200
    """
    ! BOOTSTRAP ONLY !
    Adds a new node to the cluster
    """
    # Get the parameters
    data = await request.form()
    ip = data.get('ip')
    port = data.get('port')
    address = data.get('address')
    id = len(node.ring)

    # Add node to the ring
    node.add_node_to_ring(id, ip, port, address, 0)

    # Check if all nodes have joined 
    # !! (do it after you have responded to the last node)
    t = threading.Thread(target=check_full_ring)
    t.start()

    return JSONResponse({'id': id})

def check_full_ring():
    """
    ! BOOTSTRAP ONLY !
    Checks if all nodes have been added to the ring
    """
    time.sleep(2)
    if (len(node.ring) >= total_nodes):
        node.broadcast_ring()
        node.broadcast_blockchain()
        node.broadcast_initial_nbc()
        
################## WEBSERVER #####################
uvicorn.run(app, host="0.0.0.0", port=port)

