from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class Keyboards:
    @staticmethod
    def main_menu():
        keyboard = [
            [InlineKeyboardButton("💬 Chat", callback_data="menu_chat"), InlineKeyboardButton("🎨 Image", callback_data="menu_image")],
            [InlineKeyboardButton("💰 Balance", callback_data="menu_balance"), InlineKeyboardButton("👤 Profile", callback_data="menu_profile")],
            [InlineKeyboardButton("📚 History", callback_data="menu_history"), InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")],
            [InlineKeyboardButton("🌟 Premium", callback_data="menu_premium"), InlineKeyboardButton("❓ Help", callback_data="menu_help")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_menu():
        keyboard = [
            [InlineKeyboardButton("📊 Dashboard", callback_data="admin_dashboard"), InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
            [InlineKeyboardButton("👤 Users", callback_data="admin_users"), InlineKeyboardButton("💰 Credits", callback_data="admin_credits")],
            [InlineKeyboardButton("🔧 Settings", callback_data="admin_settings"), InlineKeyboardButton("📈 Stats", callback_data="admin_stats")],
            [InlineKeyboardButton("📝 Logs", callback_data="admin_logs"), InlineKeyboardButton("💾 Backup", callback_data="admin_backup")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def model_selection():
        keyboard = [
            [InlineKeyboardButton("🤖 ChatGPT", callback_data="model_chatgpt"), InlineKeyboardButton("🧠 Gemini", callback_data="model_gemini")],
            [InlineKeyboardButton("🔮 DeepSeek", callback_data="model_deepseek"), InlineKeyboardButton("🎭 Claude", callback_data="model_claude")],
            [InlineKeyboardButton("🪐 Grok", callback_data="model_grok")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def settings_menu():
        keyboard = [
            [InlineKeyboardButton("🌐 Language", callback_data="settings_language"), InlineKeyboardButton("🎨 Theme", callback_data="settings_theme")],
            [InlineKeyboardButton("🤖 Model", callback_data="settings_model"), InlineKeyboardButton("🔙 Back", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def premium_plans():
        keyboard = [
            [InlineKeyboardButton("🌟 Basic - $5/mo", callback_data="premium_basic")],
            [InlineKeyboardButton("💎 Pro - $15/mo", callback_data="premium_pro")],
            [InlineKeyboardButton("🏆 Enterprise - $50/mo", callback_data="premium_enterprise")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def history_menu():
        keyboard = [
            [InlineKeyboardButton("📖 View History", callback_data="history_view"), InlineKeyboardButton("⭐ Favorites", callback_data="history_favorites")],
            [InlineKeyboardButton("🗑️ Delete All", callback_data="history_delete")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
