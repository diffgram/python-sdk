from pydantic import BaseModel
from typing import List

class DiffgramFile(BaseModel):
    id: int
    type: str

class Instance(BaseModel):
    id: int
