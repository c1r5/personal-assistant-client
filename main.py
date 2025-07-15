#

import asyncio
import logging
from os import getenv

from uuid import uuid4
from dotenv import load_dotenv

from assistant_agent.client import AssistantClient
from assistant_agent.agent import root_agent

from chatbot.service import ChatbotService

load_dotenv()

logger = logging.getLogger(__name__)

def getenv_or_raise(key: str) -> str:
    value = getenv(key)
    if not value:
        raise ValueError(f"{key} environment variable is not set")
    return value

async def main():
    chatbot_service_url = getenv_or_raise("CHAT_SERVICE_URL")

    chatbot_service = ChatbotService(chatbot_service_url)
    assistant_client = AssistantClient(agent=root_agent, user_id=str(uuid4()))

    await assistant_client.start_session()
    try:
        async for user_message in chatbot_service.on_user_message():
            async for assistant_message in assistant_client.request(user_message.message):
                await user_message.reply(assistant_message)

    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        await assistant_client.stop_session()
        await chatbot_service.close()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    asyncio.run(main())
