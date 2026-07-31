from typing import List, Dict
from database import Database

class ConversationMemory:
    def __init__(self, db: Database):
        self.db = db
        self.max_messages = 20
    
    def get_context(self, user_id: int, session_id: str) -> List[Dict[str, str]]:
        return self.db.get_conversation_history(user_id, session_id, self.max_messages)
    
    def add_message(self, user_id: int, session_id: str, role: str, content: str):
        self.db.save_conversation(user_id, session_id, role, content)
    
    def clear_history(self, user_id: int, session_id: str):
        pass
    
    def format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        formatted = []
        for msg in messages:
            if msg['role'] == 'user':
                formatted.append({'role': 'user', 'content': msg['content']})
            elif msg['role'] == 'assistant':
                formatted.append({'role': 'assistant', 'content': msg['content']})
        return formatted
