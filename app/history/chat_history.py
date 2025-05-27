from langchain.memory import ConversationBufferMemory

memory_store = {}

def get_chat_history(session_id: str):
    if session_id not in memory_store:
        memory_store[session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="result"
        )
    return memory_store[session_id].chat_memory