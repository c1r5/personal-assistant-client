from pydantic.main import BaseModel

class ConnectorRequest(BaseModel):
    content: str
    from_connector: str

class AgentResponse(BaseModel):
    content: str
    to_connector: str
