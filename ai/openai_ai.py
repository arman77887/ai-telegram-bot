import openai
from typing import List, Dict, Any
from config import Config
from logger.logger import logger

class OpenAIHandler:
    def __init__(self):
        self.client = openai.AsyncClient(api_key=Config.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"
        self.max_tokens = 2000
        self.temperature = 0.7
        if not Config.OPENAI_API_KEY:
            logger.warning("OpenAI API key not found")
    
    async def chat(self, messages: List[Dict[str, str]], model: str = None) -> Dict[str, Any]:
        if not Config.OPENAI_API_KEY:
            return {'error': 'OpenAI API key not configured'}
        try:
            response = await self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return {
                'content': response.choices[0].message.content,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return {'error': str(e)}
