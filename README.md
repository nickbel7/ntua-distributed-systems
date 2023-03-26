
### Semester project for the 'Distributed System' class in 9th semester at NTUA
<p align="center">
    <img src="assets/logo-white.png" alt="Noobcash" width="400"/>
<p>

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
### 1. **Bootstraping**
![bootstrapping](https://user-images.githubusercontent.com/94255085/227728144-01632b30-4df5-454a-a7d7-5060f41049f2.png)
* In order for a node in the network to be able to communicate with the others, it stores the necessary information in a dictionary structure named **ring**. By default, when a node enters the network, the ring holds no information. The node must first communicate with the **Bootstrap**. Thus it sends a post request to the Bootstrap with its ip, port and public wallet address . 
* The Bootstrap node updates its own ring with the information it receives from the other nodes. 
* The total number of nodes in the system is fixed, so once every node has entered the network the Bootstrap broadcasts the ring information to everyone along with 100 **NBCs**. 
* Now the nodes are ready to send transactions to each other. 


### 2. **Transactions**
![trxnspng](https://user-images.githubusercontent.com/94255085/227729654-36368774-da94-435c-9406-9f2b377df0a9.png)

#### 2.1 **Create and Send Transaction**
* Transactions can only be made between 2 nodes, one is the sender, the other is the receiver. 
* In order to keep track of the transactions made, each node keeps a list of **Pending Transactions** that works as a FIFO Queue. 
Everytime a new transaction arrives it is appended in the list in order to be properly processed by the node  (during the mining process).
* The node that wants to send NBCs to another, creates a new Transaction specifying the Receiver Address and the Amount it wants to transfer.
* Once the transaction is created the node signs it with its private signature, appends it to its own Pending Transactions List and then  broadcasts it to the network. 
![mining1](https://user-images.githubusercontent.com/94255085/227732053-f502c412-0e2c-41d9-9681-035afc09bcc1.png)

#### 2.2 **Receive a Transaction**
* Once a node receives a transaction by someone else, it appends it to its Pending Transactions List.

### 3. **Mining**

#### 3.1 **Preparing a block to mine**
* If the node is not already mining it starst filling up a block using transactions from the pending queue. 
* This block might be added to the blockchain, so it must be valid (up to date with the current state of the Blockchain). This means that not only the Previous Hash field of the block must refer to the hash of the last block in the chain, but the transactions it contains must be **Valid** too (the amount being transferred can be found in the sender's current state of **UTXOs**). 

![prepare_block](https://user-images.githubusercontent.com/94255085/227736506-52c56c65-1542-4192-98ab-4edab2094a76.png)

##### **Unspent Output Transactions and Transaction Validation**
* In order to be able to check this, the Blockchain Object has an attribute named UTXOs, that stores the list of **Unspent Output Transactions** of each node. The UTXOs are updated with each new addition to the blockchain in order to reflect the current state of each node's NBCs.

* When creating a new block to fill, the node also creates a deepcopy of the current UTXOs, named **Temp_UTXOs**. The node then pops transactions from the top of the pending queue validating them before adding to the block. If the transaction popped refers to an amount that can be covered by the sender's current state of UTXOs the Temp_UTXOs is updated (some of the senders UTXOs are considered spent by the viewpoint of the block) and the transaction is added to the block. 
![utxos](https://user-images.githubusercontent.com/94255085/227736703-10383964-4ccf-482f-88f3-be0d25d0815a.png)

#### 3.3 **The Mining Process**
* Once the number of transactions in the block is equal to the **capacity** of the block (which is fixed) the node can start mining the block, in hopes of finding the proper **nonce** and adding to the Blockchain.  
* If the block finds a proper nonce it adds the block to its Blockchain and broadcasts it to the other nodes in the network.
![mining2](https://user-images.githubusercontent.com/94255085/227733572-296f389b-26cf-4836-9ddc-a263f06e58c9.png)

#### 3.4 **Receiving a Valid Block mined by someone else**
* All nodes are miners, which means that there is a possibility another node manages to mine a block faster.
* In that case, the block we are trying to mine is depracated: the transactions it contains have been validated refering to a previous state of the Blockchain and UTXOs and some of them might have been present in the block that was added to the chain. 
* In order to solve this, once a **valid block** mined by someone else arrives to the node, the mining process stops. The node's Blockchain object is updated properly (chain and UTXOs) and the Temp_UTXOs list is changed to reflect the current state of the UTXOs in the system.
* The transactions that had been added to the block the node was to mine are put back to the pending transactions queue. We then check if the pending transactions list contains any of the transactions in the mined block and remove them (so as not to **doublespend** NBCs).
* The mining process can then start again from the beginning, in hopes of finding the next block to add to the chain.

![mined_block_arrival](https://user-images.githubusercontent.com/94255085/227736621-aa06e17b-f76c-4f1f-aa42-4de697e87dc1.png)

#### 3.5 **Receiving an Invalid Block. Resolving a Conflict**
* Let's assume that two nodes manage to each mine a block at the same time (a possible scenario, especially considering small difficulty values). We will refer to these two mined blocks as block_A and block_B.
* In that case, both nodes will broadcast their mined blocks at the same time. Some nodes in the network will receive block_A first and some others will receive block_B first. This means, that there are nodes in the system with different perspectives of the current UTXOs instance. 
* Furthermore, when the next block is mined it will be considered invalid by some of the nodes in the network. Let's say that the node that mined the new block had previously received block_A first. This means that the new block's previous_hash field refers to block_A. The nodes that have received block_B first, will not accept this block as it doesn't correspond to the current instance of the chain they have. 
* To resolve this, when a node receives a new mined block that has a previous_hash that doesn't refer to the last block in the node's current chain, it broadcasts a request to all nodes in the network to send back the length of the chain from their point of view. 
* The node then decides that the node that has the longest chain has the most accurate perspective of the current state of NBCs in the system and asks that node for its blockchain instance.
* The current blockchain instance is updated to reflect the longest chain found and the conflict is considred to be resolved.

![conflict](https://user-images.githubusercontent.com/94255085/227737881-7749f0d9-52c3-4234-8293-7ab49866d323.png)

## Testing the System
### The tests
After having set up the system it’s time to test it’s performance and scala-
bility.
System performance:
We set up the Noobcash system for 5 clients. After all nodes join the system,
each one reads a file that contains transactions to other nodes. All nodes per-
form the transactions from their files simultaneously.
We record the following two metrics:
• Throughput of our system, i.e., number of transactions served per unit
time.
• Block time, i.e., the average time required to add a new block to the
blockchain.
The above is recorded for the following system set up parameters:
1. capacity 1, 5, and 10
2. difficulty 4 and 5
System scalability:
We repeat the experiment for 10 clients and we will compare with the previous
results by presenting in a graph the metrics from the previous experiment
(y-axis) in relation to the number of clients (x-axis).

### Results
![Performance](https://user-images.githubusercontent.com/94255085/227796672-f12433e0-cb09-4f98-ba85-a1c4348b68af.jpg)
 

![Scalability](https://user-images.githubusercontent.com/94255085/227802461-63ccfbc2-203a-4cd5-81c9-e3fba7d2491a.jpg)

