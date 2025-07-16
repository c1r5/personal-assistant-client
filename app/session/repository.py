from typing import Callable
from typing import Awaitable
from typing_extensions import Literal
from pydantic import BaseModel
from typing import Optional

SessionID = str
Data = str

class SessionEvent(BaseModel):
    type: Literal["message", "created", "deleted"] = 'created'
    session_id: SessionID
    data: Optional[Data] = None

SessionEventListener = Callable[[SessionEvent], Awaitable[None]]

class ClientSession:
    def __init__(self, session_id: str):
        self.session_id = session_id

class SessionRepository:
    __listeners: list[SessionEventListener] = []

    def __init__(self):
        self.sessions = {}

    async def create_session(self, session_id: str):
        session = ClientSession(session_id)
        self.sessions[session_id] = session
        await self.__notify_listeners(SessionEvent(type='created', session_id=session_id))
        return session

    async def destroy_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
            await self.__notify_listeners(SessionEvent(type='deleted', session_id=session_id))

    async def get_or_create_session(self, session_id: str) -> ClientSession:
        return self.sessions.get(session_id) or await self.create_session(session_id)

    def add_session_event_listener(self, listener: SessionEventListener):
        self.__listeners.append(listener)

    async def remove_message_listener(self, listener: SessionEventListener):
        self.__listeners.remove(listener)

    async def __notify_listeners(self, event: SessionEvent):
        for listener in self.__listeners:
            await listener(event)

    async def on_message(self, message: Data, session: ClientSession):
        await self.__notify_listeners(SessionEvent(type='message', data=message, session_id=session.session_id))
