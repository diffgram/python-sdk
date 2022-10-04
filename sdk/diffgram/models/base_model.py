from fastapi import FastAPI

class DiffgramBaseModel():
    def init(self):
        pass

    def infere(self):
        raise NotImplementedError

    def get_schema(self):
        raise NotImplementedError

    def ping(self):
        pass

    def serve(self, app):
        @app.get("/infere")
        async def predict():
            return {
                "message": "Infere route"
            }

        @app.get("/get_schema")
        async def schema():
            return {
                "message": "Get schema here"
            }