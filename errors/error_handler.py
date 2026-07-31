import traceback
from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

class ErrorHandler:
    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        error = context.error
        user_id = update.effective_user.id if update and update.effective_user else None
        error_msg = f"Error: {error}\nUser ID: {user_id}\nTraceback: {traceback.format_exc()}"
        logger.error(error_msg)
        try:
            from database import Database
            db = Database()
            db.add_log('ERROR', error_msg[:500], user_id)
        except:
            pass
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ An error occurred. Please try again later."
                )
            except:
                pass
