__import__('dotenv').load_dotenv()

from uvicorn import Config, Server
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.controllers import controller, on_message, configure_cors

import signal
import asyncio
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(controller)

async def on_request_listener(message: str):
    logger.info(f"Received message: {message}")

async def run_fastapi():
    config = Config(
        app=app,
        host="0.0.0.0",  # Permitir conexões de qualquer IP
        port=5000,
        log_level="info",
        loop='asyncio'
    )
    server = Server(config)
    await server.serve()

async def main():
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    on_message.add_listener(on_request_listener)

    def shutdown():
        logger.info("Shutting down...")
        stop_event.set()

    loop.add_signal_handler(signal.SIGINT, shutdown)
    loop.add_signal_handler(signal.SIGTERM, shutdown)

    fastapi_task = asyncio.create_task(run_fastapi())

    await stop_event.wait()

    logger.info("Server stopped")

    fastapi_task.cancel()

    try:
        await asyncio.gather(fastapi_task)
    except asyncio.CancelledError:
        logger.info("Tasks cancelled successfully.")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received")
