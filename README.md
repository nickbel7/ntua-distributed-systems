
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
1. **Bootstraping**
![bootstrapping](https://user-images.githubusercontent.com/94255085/227728144-01632b30-4df5-454a-a7d7-5060f41049f2.png)
* In order for a node in the network to be able to communicate with the others, it stores the necessary information in a dictionary structure named **ring**. By default, when a node enters the network, the ring holds no information. The node must first communicate with the **Bootstrap**. Thus it sends a post request to the Bootstrap with its ip, port and public wallet address . 
* The Bootstrap node updates its own ring with the information it receives from the other nodes. 
* The total number of nodes in the system is fixed, so once every node has entered the network the Bootstrap broadcasts the ring information to everyone along with 100 **NBCs**. 
* Now the nodes are ready to send transactions to each other. 


2. **Transactions & Mining**
![trxnspng](https://user-images.githubusercontent.com/94255085/227729654-36368774-da94-435c-9406-9f2b377df0a9.png)

2.1 **Create and Send Transaction**
Transactions can only be made between 2 nodes, one is the sender the other is the receiver. 
* In order to keep track of the transactions made, each node keeps a list of **Pending Transactions** that works as a FIFO Queue. 
Everytime a new transaction arrives it is appended in the list in order to be properly processed by the node  (during the mining process).
* The node that wants to send NBCs to another, creates a new Transaction specifying the Receiver Address and the Amount it wants to transfer.
* Once the transaction is created the node signs it with its private signature, appends it to its own Pending Transactions List and then  broadcasts it to the network. 
![mining1](https://user-images.githubusercontent.com/94255085/227732053-f502c412-0e2c-41d9-9681-035afc09bcc1.png)

2.2 **Receive a Transaction**
* Once a node receives a transaction by someone else, it appends it to its Pending Transactions List.
* If the node is not already mining it starst filling up a block using transactions from the pending queue. 
* This block might be added to the blockchain, so it must be valid (up to date with the current state of the Blockchain). This means that not only the Previous Hash field of the block must refer to the hash of the last block in the chain, but the transactions it contains must be **Valid** too (the amount being transferred can be found in the sender's current state of **UTXOs**). 
* In order to be able to check this, the Blockchain Object has an attribute named UTXOs, that stores the list of **Unspent Output Transactions** of each node. The UTXOs are updated with each new addition to the blockchain in order to reflect the current state of each node's NBCs.
* ![utxos](https://user-images.githubusercontent.com/94255085/227732179-9776d321-ecbe-4799-84ae-1c9a4c9a9213.png)

* 
