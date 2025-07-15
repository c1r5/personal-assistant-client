from fastapi.routing import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from server.handlers import OnMessage
from fastapi import WebSocket
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)
controller = APIRouter()
on_message = OnMessage()

@controller.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    try:
        await websocket.accept()

        while True:
            await on_message.on_recv(websocket)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        try:
            await websocket.close()
        except Exception as e:
            logger.error(f"Error closing websocket: {e}")

def configure_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configurar com os domínios permitidos em produção
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
