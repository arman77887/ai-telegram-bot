from database import Database
from logger.logger import logger

class HistoryHandler:
    def __init__(self):
        self.db = Database()
    
    async def save_chat(self, user_id: int, message: str, response: str, model: str, tokens: int = 0):
        try:
            return self.db.add_history(user_id, message, response, model, tokens)
        except Exception as e:
            logger.error(f"Save chat error: {e}")
            return False
    
    async def get_user_history(self, user_id: int, limit: int = 50):
        try:
            return self.db.get_history(user_id, limit)
        except Exception as e:
            logger.error(f"Get history error: {e}")
            return []
    
    async def delete_history(self, user_id: int):
        try:
            return self.db.delete_history(user_id)
        except Exception as e:
            logger.error(f"Delete history error: {e}")
            return False
