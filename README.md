
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

2. Transactions + Mining
