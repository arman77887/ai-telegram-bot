from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from database import Database
from config import Config
from logger.logger import logger
from utils import admin_required
from keyboards import Keyboards

class AdminHandler:
    def __init__(self):
        self.db = Database()
    
    @admin_required
    async def admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await update.message.reply_text("🛡️ **Admin Panel**", parse_mode=ParseMode.MARKDOWN, reply_markup=Keyboards.admin_menu())
        except Exception as e:
            logger.error(f"Admin menu error: {e}")
    
    @admin_required
    async def admin_dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            stats = self.db.get_statistics()
            text = f"📊 **Dashboard**\n\n👤 Users: {stats.get('total_users', 0)}\n📈 Today: {stats.get('today_users', 0)}\n⭐ Premium: {stats.get('premium_users', 0)}\n💰 Credits: {stats.get('total_credits', 0)}\n💬 Chats: {stats.get('total_chats', 0)}"
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
    
    @admin_required
    async def search_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            args = context.args
            if not args:
                await update.message.reply_text("Usage: /search_user <id or username>")
                return
            users = self.db.search_users(args[0])
            if not users:
                await update.message.reply_text("No users found.")
                return
            text = "🔍 **Search Results**\n\n"
            for user in users[:5]:
                text += f"👤 {user['user_id']} - @{user.get('username', 'N/A')}\n"
                text += f"⭐ Premium: {'Yes' if user.get('is_premium') else 'No'}\n"
                text += f"💰 Balance: ${user.get('balance', 0):.2f}\n\n"
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Search error: {e}")
    
    @admin_required
    async def manage_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            args = context.args
            if len(args) < 2:
                await update.message.reply_text("Usage: /manage_user <action> <user_id>\n\nActions: ban, unban, delete, addpremium, removepremium")
                return
            action = args[0].lower()
            user_id = int(args[1])
            if action == 'ban':
                self.db.ban_user(user_id)
                await update.message.reply_text(f"✅ User {user_id} banned.")
            elif action == 'unban':
                self.db.unban_user(user_id)
                await update.message.reply_text(f"✅ User {user_id} unbanned.")
            elif action == 'delete':
                self.db.delete_user(user_id)
                await update.message.reply_text(f"✅ User {user_id} deleted.")
            elif action == 'addpremium':
                self.db.set_premium(user_id, 'admin_granted', 30, 0)
                await update.message.reply_text(f"✅ Premium added to {user_id}.")
            elif action == 'removepremium':
                self.db.remove_premium(user_id)
                await update.message.reply_text(f"✅ Premium removed from {user_id}.")
            else:
                await update.message.reply_text(f"❌ Unknown action: {action}")
        except Exception as e:
            logger.error(f"Manage user error: {e}")
    
    @admin_required
    async def backup_database(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            import shutil
            import os
            os.makedirs('backups', exist_ok=True)
            backup_file = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2('users.db', backup_file)
            await update.message.reply_text(f"✅ Backup created: {backup_file}")
        except Exception as e:
            logger.error(f"Backup error: {e}")
    
    @admin_required
    async def view_logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            logs = self.db.get_logs(10)
            if not logs:
                await update.message.reply_text("No logs found.")
                return
            text = "📝 **Recent Logs**\n\n"
            for log in logs:
                text += f"`{log['timestamp']}`\n{log['level']}: {log['message'][:100]}\n\n"
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Logs error: {e}")
    
    async def handle_admin_callbacks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            query = update.callback_query
            await query.answer()
            data = query.data
            if data == 'admin_dashboard':
                await self.admin_dashboard(update, context)
            elif data == 'admin_broadcast':
                await query.edit_message_text("📢 Broadcast feature coming soon.")
            elif data == 'admin_users':
                await query.edit_message_text("Use /search_user to find users.")
            elif data == 'admin_credits':
                await query.edit_message_text("💰 Credits management coming soon.")
            elif data == 'admin_settings':
                await query.edit_message_text("⚙️ Admin settings coming soon.")
            elif data == 'admin_stats':
                await self.admin_dashboard(update, context)
            elif data == 'admin_logs':
                await self.view_logs(update, context)
            elif data == 'admin_backup':
                await self.backup_database(update, context)
            elif data == 'admin_back':
                await self.admin_menu(update, context)
        except Exception as e:
            logger.error(f"Admin callback error: {e}")
