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
                for part in parts:
                    await update.message.reply_text(part, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
            return CHAT
        except Exception as e:
            logger.error(f"Chat message error: {e}")
            await update.message.reply_text("❌ Error processing.")
            return CHAT
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("❌ Cancelled.")
        return ConversationHandler.END
    
    async def model_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤖 Select AI model:", reply_markup=Keyboards.model_selection())
    
    async def model_selection_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        model = query.data.replace('model_', '')
        if model in Config.AVAILABLE_MODELS:
            if not Config.AVAILABLE_MODELS[model]['enabled']:
                await query.edit_message_text(f"❌ Model not configured.")
                return
            context.user_data['selected_model'] = model
            await query.edit_message_text(f"✅ Switched to {Config.AVAILABLE_MODELS[model]['name']}!")
        elif model == 'back_main':
            await query.edit_message_text("🔙 Main menu.", reply_markup=Keyboards.main_menu())
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_id = update.effective_user.id
            user_data = self.db.get_user(user_id)
            if not user_data:
                await update.message.reply_text("User not found.")
                return
            is_premium = self.db.is_premium(user_id)
            profile = f"👤 **Profile**\n\n🆔 ID: `{user_data['user_id']}`\n📛 Name: {user_data.get('first_name', 'N/A')}\n⭐ Premium: {'Yes' if is_premium else 'No'}\n💳 Balance: ${user_data.get('balance', 0):.2f}\n📊 Usage: {user_data.get('daily_used', 0)}/{Config.PREMIUM_DAILY_LIMIT if is_premium else Config.DAILY_FREE_LIMIT}\n🔗 Referral: `{user_data.get('referral_code', 'N/A')}`"
            await update.message.reply_text(profile, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Profile error: {e}")
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_id = update.effective_user.id
            user_data = self.db.get_user(user_id)
            if not user_data:
                await update.message.reply_text("User not found.")
                return
            balance = f"💰 **Balance**\n\n💳 Balance: ${user_data.get('balance', 0):.2f}\n📈 Earned: ${user_data.get('total_earned', 0):.2f}\n💸 Spent: ${user_data.get('total_spent', 0):.2f}"
            await update.message.reply_text(balance, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Balance error: {e}")
    
    async def premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = "🌟 **Premium Plans**\n\n💎 Pro - $15/mo\n🏆 Enterprise - $50/mo\n\n✅ Unlimited usage\n✅ All AI models\n✅ Priority support"
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=Keyboards.premium_plans())
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⚙️ Settings", reply_markup=Keyboards.settings_menu())
    
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_id = update.effective_user.id
            history = await self.history.get_user_history(user_id, 5)
            if not history:
                await update.message.reply_text("No history found.")
                return
            text = "📚 **Recent History**\n\n"
            for i, entry in enumerate(history, 1):
                text += f"{i}. {entry['message'][:50]}...\n📅 {entry['timestamp']}\n\n"
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=Keyboards.history_menu())
        except Exception as e:
            logger.error(f"History error: {e}")
    
    async def delete_history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if await self.history.delete_history(user_id):
            await update.message.reply_text("✅ History deleted.")
        else:
            await update.message.reply_text("❌ Failed to delete history.")
    
    async def referral_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_id = update.effective_user.id
            stats = await self.referral.get_referral_stats(user_id)
            text = f"🔄 **Referral System**\n\n👥 Referrals: {stats.get('total_referrals', 0)}\n💰 Earned: ${stats.get('total_earned', 0):.2f}\n🔗 Code: `{stats.get('referral_code', 'N/A')}`\n\nShare: https://t.me/{context.bot.username}?start={stats.get('referral_code', '')}"
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Referral error: {e}")
    
    async def clear_memory(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        session_id = context.user_data.get('session_id')
        if session_id:
            self.memory.clear_history(update.effective_user.id, session_id)
            context.user_data['session_id'] = None
            await update.message.reply_text("🧹 Memory cleared.")
        else:
            await update.message.reply_text("No active conversation.")
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.admin_handler.admin_menu(update, context)
    
    async def image_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🎨 Image generation - Send prompt.")
    
    async def vision_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔍 Vision AI - Send image.")
    
    async def pdf_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📄 PDF Chat - Send PDF.")
    
    async def voice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🗣️ Voice - Send voice message.")
    
    async def translate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🌐 Translate - Send text.")
    
    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("❌ Unknown command. Use /help")
    
    async def handle_callbacks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            query = update.callback_query
            await query.answer()
            data = query.data
            if data == "back_main":
                await query.edit_message_text("Main menu.", reply_markup=Keyboards.main_menu())
            elif data.startswith("model_"):
                await self.model_selection_callback(update, context)
            elif data == "settings_language":
                await query.edit_message_text("🌐 Language selection coming soon.")
            elif data == "settings_theme":
                await query.edit_message_text("🎨 Theme selection coming soon.")
            elif data.startswith("premium_"):
                await query.edit_message_text("🌟 Premium payment coming soon.")
            elif data == "history_delete":
                await self.delete_history_command(update, context)
            elif data == "history_view":
                await self.history_command(update, context)
            elif data.startswith("admin_"):
                await self.admin_handler.handle_admin_callbacks(update, context)
            else:
                await query.edit_message_text("Unknown action.")
        except Exception as e:
            logger.error(f"Callback error: {e}")
