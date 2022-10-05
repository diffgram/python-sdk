from pydantic import BaseModel
from typing import Optional, List, Literal
class DiffgramFile(BaseModel):
    id: int
    type: Literal['image', 'frame', 'video', 'text', 'audio', 'sensor_fusion', 'geospatial']

class Attribute(BaseModel):
    id: int
class Instance(BaseModel):
    id: int

class Prediction(BaseModel):
    instances: Optional[List[Instance]]
    attributes: Optional[List[Attribute]]

