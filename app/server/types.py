from typing_extensions import Literal
from pydantic import BaseModel, RootModel

class KeyInfo(BaseModel):
    connector_name: str
    permitted_endpoints: Literal['ws']

class APIKeys(RootModel):
    root: dict[str, KeyInfo]

    def __setitem__(self, key: str, value: KeyInfo):
        self.root[key] = value

    def __getitem__(self, key: str) -> KeyInfo:
        return self.root[key]

    def __delitem__(self, key: str):
        del self.root[key]
