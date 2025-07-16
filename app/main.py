__import__('dotenv').load_dotenv()

from uvicorn import Config, Server
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from session.repository import SessionEvent
from server.controllers import controller, session_repository
from agents.client import AgentClient

import signal
import asyncio
import logging

logger = logging.getLogger(__name__)

app = FastAPI()
agent = AgentClient()
# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(controller)

async def on_create_session(session_id: str):
    await agent.create_session(session_id)

async def on_delete_session(session_id: str):
    await agent.delete_session(session_id)

async def on_session_message(session_id: str, message: str):
    ...
    # async for response in agent.request(session_id, message):
    #     logger.info(f"Agent response: {response}")

async def on_request_listener(event: SessionEvent):
    match event.type:
        case "message":
            if event.data is not None:
                await on_session_message(event.session_id, event.data)
        case "created":
            logger.info(f"Session created: {event.session_id}")
            await agent.create_session(event.session_id)
        case "deleted":
            logger.info(f"Session deleted: {event.session_id}")
            await agent.delete_session(event.session_id)
        case _:
            logger.warning(f"Unknown event type: {event.type}")

async def main():
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    server = None

    session_repository.add_session_event_listener(on_request_listener)

    async def shutdown():
        logger.info("Shutting down...")
        if server:
            logger.info("Stopping server...")
            await server.shutdown()
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))

    config = Config(
        app=app,
        host="0.0.0.0",
        port=5000,
        log_level="info",
        loop='asyncio',
        reload=True
    )
    server = Server(config)
    server_task = asyncio.create_task(server.serve())

    try:
        await stop_event.wait()
        logger.info("Stop event received")

        await asyncio.wait_for(server_task, timeout=5.0)
        logger.info("Server stopped gracefully")
    except asyncio.TimeoutError:
        logger.warning("Server shutdown timed out, forcing exit")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    finally:
        await asyncio.sleep(0.1)  # Give pending tasks a chance to complete
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received")
