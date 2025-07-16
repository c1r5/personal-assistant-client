from fastapi.routing import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket
from fastapi import FastAPI

import logging

from server.security import key_exists
from session.repository import SessionRepository

logger = logging.getLogger(__name__)

controller = APIRouter()
session_repository = SessionRepository()

@controller.websocket("/ws/{api_key}")
async def websocket_handler(websocket: WebSocket, api_key: str):
    try:
        if not key_exists(api_key):
            await websocket.close(403)
            return

        await websocket.accept()

        session = await session_repository.create_session(api_key)

        async def on_reply_listener(data):
            await websocket.send_text(data)

        session.add_on_reply_listener(on_reply_listener)

        while True:
            data = await websocket.receive_text()
            await session.on_message(data)


    except Exception as e:
        logger.error(f"Error in websocket_handler: {e}")
    finally:
        await websocket.close()

def configure_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configurar com os domínios permitidos em produção
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
