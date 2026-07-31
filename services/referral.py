from database import Database
from config import Config
from logger.logger import logger

class ReferralHandler:
    def __init__(self):
        self.db = Database()
    
    async def get_referral_stats(self, user_id: int):
        try:
            user_data = self.db.get_user(user_id)
            return {
                'total_referrals': user_data.get('total_referrals', 0) if user_data else 0,
                'total_earned': 0,
                'referral_code': user_data.get('referral_code', 'N/A') if user_data else 'N/A'
            }
        except Exception as e:
            logger.error(f"Referral stats error: {e}")
            return {}
