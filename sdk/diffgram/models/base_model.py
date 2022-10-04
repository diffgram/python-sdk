from .model_interfaces import DiffgramFile, Prediction, Attribute, Instance
class DiffgramBaseModel():
    def init(self):
        pass

    def infere(self, file: DiffgramFile) -> Prediction:
        raise NotImplementedError

    def get_schema(self):
        raise NotImplementedError

    def ping(self):
        pass

    def serve(self, app):
        @app.post("/infere")
        async def predict(file: DiffgramFile):
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
        async def schema():
            return {
                "message": "Get schema here"
            }