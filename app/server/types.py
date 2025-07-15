from typing_extensions import Literal
from pydantic.main import BaseModel

class KeyInfo(BaseModel):
    connector_name: str
    permitted_endpoints: Literal['ws']

class APIKeys(BaseModel):
    __root__: dict[str, KeyInfo]

    def __setitem__(self, key: str, value: KeyInfo):
        self.__root__[key] = value

    def __getitem__(self, key: str) -> KeyInfo:
        return self.__root__[key]

    def __delitem__(self, key: str):
        del self.__root__[key]
