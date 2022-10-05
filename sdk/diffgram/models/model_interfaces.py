from pydantic import BaseModel, AnyUrl, validator
from typing import Optional, List, Literal

class DiffgramImage(BaseModel):
    height: int
    width: int
    url_signed: AnyUrl

class DiffgramText(BaseModel):
    tokens_url_signed: AnyUrl

class DiffgramFile(BaseModel):
    id: int
    original_filename: str
    image: Optional[DiffgramImage]
    text: Optional[DiffgramText]
    type: Literal['image', 'frame', 'video', 'text', 'audio', 'sensor_fusion', 'geospatial']

    @validator('type')
    def requre_object_if_type(cls, type, values):
        file_object = values.get(type)

        if not file_object:
            raise ValueError(f"{type} is missing in the payload")

        return type
        

class Attribute(BaseModel):
    id: int
class Instance(BaseModel):
    id: int

class Prediction(BaseModel):
    instances: Optional[List[Instance]]
    attributes: Optional[List[Attribute]]

