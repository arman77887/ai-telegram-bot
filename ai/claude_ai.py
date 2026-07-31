import httpx
import json
from typing import List, Dict, Any
from config import Config
from logger.logger import logger

class ClaudeHandler:
    def __init__(self):
        self.api_key = Config.CLAUDE_API_KEY
        self.base_url = "https://api.anthropic.com/v1"
        self.model = "claude-3-haiku-20240307"
        self.max_tokens = 2000
        self.temperature = 0.7
        if not self.api_key:
            logger.warning("Claude API key not found")
    
    async def chat(self, messages: List[Dict[str, str]], model: str = None) -> Dict[str, Any]:
        if not self.api_key:
            return {'error': 'Claude API key not configured'}
        try:
            claude_messages = []
            system = None
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if role == 'system':
                    system = content
                else:
                    claude_messages.append({'role': role, 'content': content})
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                    json={"model": model or self.model, "messages": claude_messages, "max_tokens": self.max_tokens, "temperature": self.temperature, "system": system},
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return {'content': data['content'][0]['text']}
                else:
                    return {'error': f"HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"Claude error: {e}")
            return {'error': str(e)}
