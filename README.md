
### Semester project for the 'Distributed System' class in 9th semester at NTUA

### Tools Used + [Dependencies](https://github.com/nickbel7/ntua-distributed-systems/blob/master/requirements.txt)
1. Python 3.7
2. Docker
3. FastAPI

## Deployment
### 🐳 Docker
1. Build the image <br>
   `docker build -t ntua-distributed-systems .`
2. Run the container in the specified port (ex. 8000) <br>
   `docker run -e PORT=8000 -e IP=127.0.0.1 -p 8000:8000 --rm ntua-distributed-systems`
### 🖥️ VM (python 3.7 installed)
1. Install requirement <br>
    `pip install -r requirements`
2. Run the entrypoint (api.py) in a specified port (ex.8000)
    `python api.py --port 8000`

## Structure
### 1. External Files
 - `api.py` :  Entrypoint + API routes
 - `client.py` : CLI tool
### 2. Internal Files
- `.env` : Initialization parameters
-  `node.py` : Business logic + State of node
-  `transaction.py` : Definition of Transaction + relevant methods
-  `blockchain.py` : Definition of Blockchain + relevant methods
-  `block.py` : Definition of Block + relevant methods
-  `wallet.py` : Definition of Wallet
-  `utxo.py` : Definition of UTXO

## How it works
1. Bootstraping
![bootstrapping](https://user-images.githubusercontent.com/94255085/227728144-01632b30-4df5-454a-a7d7-5060f41049f2.png)
* In order for a node in the network to be able to communicate with the others, it stores the necessary information in a dicionary structure named ring. By default, when a node enters the network, the ring holds no information. The node must first communicate with the Bootstrap. Thus it sends a post request to the Bootstrap with its ip, port and public wallet address . 
* The Bootstrap node updates its own ring with the information it receives from the other nodes. 
* The total number of nodes in the system is fixed, so once every node has entered the network the Bootstrap broadcasts the ring information to everyone along with 100 NBCs. 
* Now the nodes are ready to send transactions to each other. 


2. Transactions + Mining
![trxnspng](https://user-images.githubusercontent.com/94255085/227729379-1cfbc117-d2ec-4a1d-af82-05959594044e.png)
* Transactions can only be made between 2 nodes, one is the sender the other is the receiver. 
* In order to keep track of the transactions made, each node keeps a list of **Pending Transactions**. 
Everytime a new transaction arrives it is appended in the list in order to be properly processed by the node  (during the mining process).
* The node that wants to send NBCs to another, creates a new Transaction specifying the Receiver Address and the Amount it wants to transfer.
* Once the transaction is created the node signs it with its private signature, appends it to its own Pending Transactions List and then  broadcasts it to the network. 
