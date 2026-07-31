from database import Database
from logger.logger import logger

class PaymentHandler:
    def __init__(self):
        self.db = Database()
    
    async def process_premium_payment(self, update, context, plan):
        try:
            await update.callback_query.edit_message_text(
                f"🌟 Payment for {plan} plan coming soon.\n"
                "Currently in development."
            )
        except Exception as e:
            logger.error(f"Payment error: {e}")
