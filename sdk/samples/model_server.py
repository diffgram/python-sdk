from diffgram import DiffgramBaseModel
from fastapi import FastAPI

app = FastAPI()

DiffgramBaseModel().serve(app)