import re
import hashlib
import random
import string
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class Utils:
    @staticmethod
    def generate_session_id(user_id: int) -> str:
        timestamp = datetime.now().timestamp()
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        raw = f"{user_id}{timestamp}{random_str}"
        return hashlib.md5(raw.encode()).hexdigest()
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
    
    @staticmethod
    def escape_markdown(text: str) -> str:
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return ''.join(f'\\{char}' if char in escape_chars else char for char in text)
