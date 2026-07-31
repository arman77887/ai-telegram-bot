#!/usr/bin/env python
import asyncio
import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters, ContextTypes
from config import Config
from database import Database
from handlers import MainHandlers, CHAT
from admin import AdminHandler
from errors.error_handler import ErrorHandler
import signal

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class AITelegramBot:
    def __init__(self):
        self.application = None
        self.handlers = MainHandlers()
        self.admin_handler = AdminHandler()
        self.db = Database()
        self.is_running = False
        self.error_handler = ErrorHandler()
    
    def build_application(self):
        try:
            self.application = Application.builder().token(Config.BOT_TOKEN).build()
            self.setup_handlers()
            logger.info("Application built successfully")
            return self.application
        except Exception as e:
            logger.error(f"Error building application: {e}")
            raise
    
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("admin", self.handlers.admin_command))
        self.application.add_handler(CommandHandler("start", self.handlers.start))
        self.application.add_handler(CommandHandler("help", self.handlers.help_command))
        self.application.add_handler(CommandHandler("chat", self.handlers.chat_command))
        self.application.add_handler(CommandHandler("cancel", self.handlers.cancel))
        self.application.add_handler(CommandHandler("model", self.handlers.model_command))
        self.application.add_handler(CommandHandler("profile", self.handlers.profile_command))
        self.application.add_handler(CommandHandler("balance", self.handlers.balance_command))
        self.application.add_handler(CommandHandler("premium", self.handlers.premium_command))
        self.application.add_handler(CommandHandler("settings", self.handlers.settings_command))
        self.application.add_handler(CommandHandler("history", self.handlers.history_command))
        self.application.add_handler(CommandHandler("deletehistory", self.handlers.delete_history_command))
        self.application.add_handler(CommandHandler("referral", self.handlers.referral_command))
        self.application.add_handler(CommandHandler("clearmemory", self.handlers.clear_memory))
        
        chat_conv = ConversationHandler(
            entry_points=[CommandHandler('chat', self.handlers.chat_command)],
            states={CHAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.chat_message)]},
            fallbacks=[CommandHandler('cancel', self.handlers.cancel)],
            allow_reentry=True
        )
        self.application.add_handler(chat_conv)
        self.application.add_handler(CallbackQueryHandler(self.handlers.handle_callbacks))
        self.application.add_handler(MessageHandler(filters.COMMAND, self.handlers.unknown))
        self.application.add_error_handler(self.error_handler.handle_error)
    
    async def initialize_bot(self):
        try:
            bot = self.application.bot
            commands = [
                ("start", "Start the bot"), ("help", "Show help"), ("chat", "Start AI chat"),
                ("model", "Switch AI model"), ("profile", "View profile"), ("balance", "Check balance"),
                ("premium", "Premium subscription"), ("settings", "Bot settings"), ("history", "View history"),
                ("deletehistory", "Delete history"), ("referral", "Referral system"), ("clearmemory", "Clear memory")
            ]
            await bot.set_my_commands(commands)
            bot_info = await bot.get_me()
            logger.info(f"Bot started as: @{bot_info.username}")
            return True
        except Exception as e:
            logger.error(f"Error initializing bot: {e}")
            return False
    
    async def shutdown(self):
        logger.info("Shutting down bot...")
        self.is_running = False
        if self.application:
            try:
                await self.application.stop()
                await self.application.shutdown()
                logger.info("Application stopped")
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
    
    def signal_handler(self, signum, frame):
        logger.info(f"Received signal {signum}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.shutdown())
        finally:
            loop.close()
            sys.exit(0)
    
    async def run(self):
        try:
            self.build_application()
            await self.initialize_bot()
            logger.info("Starting bot...")
            self.is_running = True
            await self.application.start()
            await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            logger.info("Bot is running! Press Ctrl+C to stop.")
            while self.is_running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise
        finally:
            await self.shutdown()
    
    def run_sync(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        try:
            asyncio.run(self.run())
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)

def main():
    if not Config.BOT_TOKEN:
        logger.error("No bot token found. Please set BOT_TOKEN in .env file")
        sys.exit(1)
    bot = AITelegramBot()
    bot.run_sync()

if __name__ == "__main__":
    main()
