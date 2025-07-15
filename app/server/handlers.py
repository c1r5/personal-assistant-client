from fastapi.websockets import WebSocket
from typing import Callable
from typing import Awaitable
import json

OnRequestListener = Callable[[str], Awaitable[None]]

class OnMessage:
    def __init__(self):
        self.__listeners = []

    def add_listener(self, listener: OnRequestListener):
        self.__listeners.append(listener)

    async def on_recv(self, websocket: WebSocket):
        message = await websocket.receive_text()
        if await self.__is_request(message):
            await self.on_request(message)
        else:
            await self.__on_message(websocket, message)

    async def on_request(self, message: str):
        for listener in self.__listeners:
            await listener(message)

    async def __on_message(self, websocket: WebSocket, message: str):
        match message:
            case "ping":
                await websocket.send_text("pong")
            case "bye":
                await websocket.send_text("goodbye")
                await websocket.close()
            case _:
                return

    async def __is_request(self, message: str) -> bool:
        try:
            json.loads(message)
            return True
        except json.JSONDecodeError:
            return False
