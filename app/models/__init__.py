from pydantic.main import BaseModel

class ClientMessage(BaseModel):
    content: str
    connector: str
