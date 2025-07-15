__import__('dotenv').load_dotenv()

from uvicorn import Config, Server
from fastapi import FastAPI

from app.server.controllers import controller

import signal
from app.server.controllers import on_message
import asyncio
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(controller)

async def on_request_listener(message: str):
    ...

async def run_fastapi():
    config = Config("main:app", port=5000, log_level="info")
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
        logger.info("Tarefas canceladas com sucesso.")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received")
