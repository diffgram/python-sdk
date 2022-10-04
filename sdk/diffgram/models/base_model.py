from .model_interfaces import DiffgramFile, Instance
from typing import List
class DiffgramBaseModel():
    def init(self):
        pass

    def infere(self, file: DiffgramFile) -> List[Instance]:
        raise NotImplementedError

    def get_schema(self):
        raise NotImplementedError

    def ping(self):
        pass

    def serve(self, app):
        @app.post("/infere")
        async def predict(file: DiffgramFile):
            predictions = self.infere(file)

            if not isinstance(predictions, List):
                raise ValueError('infere should return List of type Instance') 

            for prediction in predictions:
                res = isinstance(prediction, Instance)
                if not res:
                    raise ValueError('infere should return List of type Instance') 

            return {
                "file": file,
                "predictions": predictions
            }

        @app.get("/get_schema")
        async def schema():
            return {
                "message": "Get schema here"
            }