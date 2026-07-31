import google.generativeai as genai
from typing import List, Dict, Any
import asyncio
from config import Config
from logger.logger import logger

class GeminiHandler:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = "gemini-pro"
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            logger.warning("Gemini API key not found")
            self.model = None
    
    async def chat(self, messages: List[Dict[str, str]], model: str = None) -> Dict[str, Any]:
        if not self.api_key:
            return {'error': 'Gemini API key not configured'}
        try:
            prompt = ""
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if role == 'system':
                    prompt += f"System: {content}\n"
                elif role == 'user':
                    prompt += f"User: {content}\n"
                elif role == 'assistant':
                    prompt += f"Assistant: {content}\n"
            response = await asyncio.get_event_loop().run_in_executor(None, lambda: self.model.generate_content(prompt))
            return {'content': response.text}
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return {'error': str(e)}
