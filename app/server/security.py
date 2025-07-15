import uuid

from app.server.types import APIKeys
from app.server.types import KeyInfo

def generate_api_key():
    return str(uuid.uuid4())

def save_api_key(api_key: str, key_info: KeyInfo):
    with open('api_keys.json', 'a') as f:

        api_keys = APIKeys.model_validate_json(f.read())

        api_keys[api_key] = key_info

        f.write(APIKeys.model_dump_json(api_keys))

def load_api_keys() -> APIKeys:
    with open('api_keys.json', 'r') as f:
        return APIKeys.model_validate_json(f.read())

def get_api_key_info(api_key: str) -> KeyInfo:
    api_keys = load_api_keys()
    return api_keys[api_key]
