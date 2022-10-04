from pydantic import BaseModel
from typing import Optional
from typing import List

class DiffgramFile(BaseModel):
    id: int
    type: str

class Attribute(BaseModel):
    id: int
class Instance(BaseModel):
    id: int

class Prediction(BaseModel):
    instances: Optional[List[Instance]]
    attributes: Optional[List[Attribute]]

