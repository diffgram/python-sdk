from diffgram import DiffgramBaseModel, Prediction, Instance, Attribute
from fastapi import FastAPI
class MyTestModel(DiffgramBaseModel):
    def infere(self, file):
        return Prediction(
            instances=[Instance(id=1)],
            attributes=[Attribute(id=1)]
        )

    def get_schema(self):
        return super().get_schema()

app = FastAPI()
MyTestModel(allowed_types=["image"]).serve(app)