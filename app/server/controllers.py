from fastapi.routing import APIRouter
from app.server.handlers import OnMessage
from app.server.security import get_api_key_info
from fastapi import WebSocket

controller = APIRouter()
on_message = OnMessage()

controller.websocket("/ws/{api_key}", name="Websocket")
async def websocket_handler(websocket: WebSocket, api_key: str):

    api_key_info = get_api_key_info(api_key)

    if not api_key_info:
        await websocket.close(code=403)
        return

    await websocket.accept()

    try:
        while True:
            await on_message.on_recv(websocket)

    except Exception as e:
        print(e)
