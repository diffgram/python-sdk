from abc import ABC, abstractmethod
from fastapi import HTTPException
from typing import Literal
from .model_interfaces import DiffgramFile, Prediction, Attribute, Instance
class DiffgramBaseModel(ABC):
    diffgram_allowed_types = Literal['image', 'frame', 'video', 'text', 'audio', 'sensor_fusion', 'geospatial']
    allowed_types: list = None
    
    def __init__(
        self, 
        allowed_types: list = None,
    ):
        if allowed_types is not None:
            if not isinstance(allowed_types, list):
                raise ValueError('allowed_types must be of type list')

            for allowed_type in allowed_types:
                if allowed_type not in self.diffgram_allowed_types.__dict__['__args__']:
                    raise ValueError(f"{allowed_type} is not valid Diffgram file type")
            
            self.allowed_types = allowed_types

    @abstractmethod
    def infere(self, file: DiffgramFile) -> Prediction:
        raise NotImplementedError

    @abstractmethod
    def get_schema(self):
        raise NotImplementedError

    def serve(self, app):
        @app.post("/infere")
        async def infere_route(file: DiffgramFile):
            if self.allowed_types is not None:
                if file.type not in self.allowed_types:
                    raise HTTPException(status_code=404, detail=f"This model does not support {file.type} files")

            predictions = self.infere(file)

            if not isinstance(predictions, Prediction):
                raise ValueError('predictions should be of type Prediction') 

            if predictions.instances:
                for predicted_instance in predictions.instances:
                    instance = isinstance(predicted_instance, Instance)
                    if not instance:
                        raise ValueError('predicted instances should be of type Instance')

            if predictions.attributes:
                for predicted_attributes in predictions.attributes:
                    instance = isinstance(predicted_attributes, Attribute)
                    if not instance:
                        raise ValueError('predicted attributes should be of type Attribute')

            return {
                "file": file,
                "predictions": predictions
            }

        @app.get("/get_schema")
        async def get_schema_route():
            return {
                "message": "Get schema here"
            }

        @app.get("/ping")
        async def ping_route():
            return {
                "message": "Model is up and running"
            }