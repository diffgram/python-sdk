from diffgram import DiffgramBaseModel, Instance
from fastapi import FastAPI

class MyTestModel(DiffgramBaseModel):
    def infere(self, file):
        return [
            Instance(id=1)
        ]

    def get_schema(self):
        return super().get_schema()

app = FastAPI()
MyTestModel().serve(app)