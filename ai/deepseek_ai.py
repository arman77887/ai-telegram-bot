import httpx
import json
from typing import List, Dict, Any
from config import Config
from logger.logger import logger

class DeepSeekHandler:
    def __init__(self):
        self.api_key = Config.DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"
        self.max_tokens = 2000
        self.temperature = 0.7
        if not self.api_key:
            logger.warning("DeepSeek API key not found")
    
    async def chat(self, messages: List[Dict[str, str]], model: str = None) -> Dict[str, Any]:
        if not self.api_key:
            return {'error': 'DeepSeek API key not configured'}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={"model": model or self.model, "messages": messages, "max_tokens": self.max_tokens, "temperature": self.temperature},
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return {'content': data['choices'][0]['message']['content']}
                else:
                    return {'error': f"HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"DeepSeek error: {e}")
            return {'error': str(e)}
