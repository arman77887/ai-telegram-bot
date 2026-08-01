import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is required")
    
    ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    GROK_API_KEY = os.getenv('GROK_API_KEY')
    
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///users.db')
    
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    MAINTENANCE_MODE = os.getenv('MAINTENANCE_MODE', 'False').lower() == 'true'
    DAILY_FREE_LIMIT = int(os.getenv('DAILY_FREE_LIMIT', 5))
    PREMIUM_DAILY_LIMIT = int(os.getenv('PREMIUM_DAILY_LIMIT', 50))
    REFERRAL_BONUS = int(os.getenv('REFERRAL_BONUS', 10))
    REFERRAL_COMMISSION = float(os.getenv('REFERRAL_COMMISSION', 0.1))
    
    AVAILABLE_MODELS = {
        'chatgpt': {'name': 'ChatGPT', 'enabled': bool(OPENAI_API_KEY)},
        'gemini': {'name': 'Gemini', 'enabled': bool(GEMINI_API_KEY)},
        'deepseek': {'name': 'DeepSeek', 'enabled': bool(DEEPSEEK_API_KEY)},
        'claude': {'name': 'Claude', 'enabled': bool(CLAUDE_API_KEY)},
        'grok': {'name': 'Grok', 'enabled': bool(GROK_API_KEY)}
    }
    
    DEFAULT_MODEL = 'gemini'
