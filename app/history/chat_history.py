from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory

memory_store = {}

def get_chat_history(session_id: str):
    if session_id not in memory_store:
        memory_store[session_id] = ChatMessageHistory()
    return memory_store[session_id]