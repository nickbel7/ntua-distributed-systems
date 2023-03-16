from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware

import node

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

@app.get("/")
async def root():
    return {"message": "Welcome to Noobcoin"}

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