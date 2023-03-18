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
args = argParser.parse_args()

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
# IP ADDRESS
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip_address = s.getsockname()[0]
print('IP address: ', ip_address) # debug
s.close()
# PORT
port = args.port
print('PORT: ', port) # debug 
node.ip = ip_address
node.port = port

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
    # Defines the genesis block
    gen_block = node.create_new_block()
    gen_block.nonce = 0

    # Add initial transaction to the genesis block
    first_transaction = Transaction(
        sender_address='0', sender_private_key=None, receiver_address = node.wallet.address,  
        value = 100 * int(os.getenv('TOTAL_NODES'))
    )
    first_transaction.calculate_hash()

    gen_block.transactions_list.append(first_transaction)
    gen_block.myHash()

    # Add genesis block to the chain
    node.blockchain.chain.append(gen_block)
    
    # print("RING AFTER CREATION OF GENESIS BLOCK")
    # print(node.ring)

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
    node.ring = await request.json()
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
    # Fetch transaction data
    data = await request.body()
    new_transaction = pickle.loads(data)

    # Add transaction to block
    node.add_transaction_to_block(new_transaction)

    print("Transaction received")

    # print("RING AFTER RECEPTION OF TRANSACTION")
    # print(node.ring)
    

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

    # print("RING AFTER INSERTION OF NODE")
    # print(node.ring)

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

