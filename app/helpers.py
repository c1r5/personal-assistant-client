from os import getenv

def getenv_or_raise(key: str) -> str:
    value = getenv(key)
    if not value:
        raise ValueError(f"{key} environment variable is not set")
    return value
