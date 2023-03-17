from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import socket
import jsonify
import uvicorn
import argparse

from node import Node

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
total_nodes = os.getenv('TOTAL_NODES')
total_nbc = 100 * total_nodes

bootstrap_node = {
    'ip': os.getenv('BOOTSTRAP_IP'),
    'port': os.getenv('BOOTSTRAP_PORT')
}

# Step 3.
# Decide if node is the Bootstrap node
# 3.1 Get the ip address, port
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip_address = s.getsockname()[0]
print(ip_address)
s.close()
port = args.port
print(port)
node.ip = ip_address
node.port = port

# 3.2 See if it matches the corresponding ip and port
if (ip_address == bootstrap_node["ip"] and port == bootstrap_node["port"]):
    node.is_bootstrap = True

# Step 4.
# Register node to the cluster
if (node.is_bootstrap):
    node.id = 0
    node.add_node_to_ring(node.ip, node.port, node.wallet.address, total_nbc)
    print(node.ring)
else:
    node.unicast_node(bootstrap_node)

################## ROUTES #####################
@app.get("/")
async def root():
    return {"message": f"Welcome to Noobcoin. I am {socket.gethostname()} : {socket.gethostbyname(socket.gethostname())}"}

@app.post("/get_ring")
async def get_ring():
    """
    Gets the completed list of nodes from Bootstrap node
    """

@app.post("/get_blockchain")
async def get_blockchain():
    """
    Gets the lastest version of the blockchain from the Bootstrap node
    """
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
    node.add_node_to_ring(ip, port, address, 0)
    print(node.ring)

    # Check if all nodes have joined
    check_full_ring()

    return jsonify({'id': id})


def check_full_ring():
    """
    ! BOOTSTRAP ONLY !
    Checks if all nodes have been added to the ring
    """
    if len(node.ring == total_nodes):
        node.broadcast_ring
        node.broadcast_blockchain
        # node.broadcast_initial_nbc
        
################## WEBSERVER #####################
uvicorn.run(app, host="0.0.0.0", port=port)

