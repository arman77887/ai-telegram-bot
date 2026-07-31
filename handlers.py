from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from datetime import datetime
import json
import io
from database import Database
from config import Config
from logger.logger import logger
from utils import Utils
from keyboards import Keyboards
from ai.openai_ai import OpenAIHandler
from ai.gemini_ai import GeminiHandler
from ai.deepseek_ai import DeepSeekHandler
from ai.claude_ai import ClaudeHandler
from ai.grok_ai import GrokHandler
from ai.memory import ConversationMemory
from services.history import HistoryHandler
from services.referral import ReferralHandler
from admin import AdminHandler

CHAT = 1

class MainHandlers:
    def __init__(self):
        self.db = Database()
        self.admin_handler = AdminHandler()
        self.openai = OpenAIHandler()
        self.gemini = GeminiHandler()
        self.deepseek = DeepSeekHandler()
        self.claude = ClaudeHandler()
        self.grok = GrokHandler()
        self.memory = ConversationMemory(self.db)
        self.history = HistoryHandler()
        self.referral = ReferralHandler()
        self.default_model = Config.DEFAULT_MODEL
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user = update.effective_user
            user_id = user.id
            referral_code = context.args[0] if context.args else None
            self.db.register_user(user_id, user.username, user.first_name, user.last_name, user.language_code, referral_code)
            welcome = f"👋 Welcome {user.first_name or 'User'}!\n\n🤖 AI Bot with multiple AI models.\n\nCommands:\n/chat - Chat with AI\n/image - Generate image\n/profile - View profile\n/balance - Check balance\n/premium - Upgrade\n/help - Get help"
            await update.message.reply_text(welcome, parse_mode=ParseMode.MARKDOWN, reply_markup=Keyboards.main_menu())
        except Exception as e:
            logger.error(f"Start error: {e}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = "❓ **Help Center**\n\n/start - Start bot\n/help - Show help\n/chat - AI chat\n/image - Generate image\n/model - Switch model\n/profile - View profile\n/balance - Check balance\n/premium - Premium subscription\n/settings - Bot settings\n/history - View history\n/deletehistory - Delete history\n/referral - Referral system"
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN, reply_markup=Keyboards.main_menu())
    
    async def chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_id = update.effective_user.id
            user = self.db.get_user(user_id)
            if user and user.get('is_banned'):
                await update.message.reply_text("🚫 You are banned.")
                return
            daily_used = self.db.get_daily_usage(user_id)
            is_premium = self.db.is_premium(user_id)
            daily_limit = Config.PREMIUM_DAILY_LIMIT if is_premium else Config.DAILY_FREE_LIMIT
            if daily_used >= daily_limit:
                await update.message.reply_text(f"🚫 Daily limit reached! ({daily_limit} messages)\nUpgrade to premium.")
                return
            model = context.user_data.get('selected_model', self.default_model)
            session_id = context.user_data.get('session_id')
            if not session_id:
                session_id = Utils.generate_session_id(user_id)
                context.user_data['session_id'] = session_id
            await update.message.reply_text(f"💬 **Chat Mode**\nModel: {model}\nUsage: {daily_used}/{daily_limit}\n\nSend your message.", parse_mode=ParseMode.MARKDOWN)
            return CHAT
        except Exception as e:
            logger.error(f"Chat command error: {e}")
            return ConversationHandler.END
    
    async def chat_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_id = update.effective_user.id
            message_text = update.message.text
            if not message_text:
                await update.message.reply_text("Please send text.")
                return CHAT
            self.db.update_user_usage(user_id)
            session_id = context.user_data.get('session_id')
            if not session_id:
                session_id = Utils.generate_session_id(user_id)
                context.user_data['session_id'] = session_id
            model = context.user_data.get('selected_model', self.default_model)
            self.memory.add_message(user_id, session_id, 'user', message_text)
            context_messages = self.memory.get_context(user_id, session_id)
            formatted_messages = self.memory.format_messages(context_messages)
            response = None
            if model == 'chatgpt':
                response = await self.openai.chat(formatted_messages)
            elif model == 'gemini':
                response = await self.gemini.chat(formatted_messages)
            elif model == 'deepseek':
                response = await self.deepseek.chat(formatted_messages)
            elif model == 'claude':
                response = await self.claude.chat(formatted_messages)
            elif model == 'grok':
                response = await self.grok.chat(formatted_messages)
            else:
                response = {'error': 'Unsupported model'}
            if 'error' in response:
                await update.message.reply_text(f"❌ Error: {response['error']}")
                return CHAT
            self.memory.add_message(user_id, session_id, 'assistant', response['content'])
            await self.history.save_chat(user_id, message_text, response['content'], model)
            response_text = response['content']
            if len(response_text) > 4000:
                parts = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
                for part in parts
