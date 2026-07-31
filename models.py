from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: str = "en"
    registration_date: datetime = None
    is_premium: bool = False
    premium_expiry: Optional[datetime] = None
    daily_used: int = 0
    theme: str = "light"
    is_banned: bool = False
    referral_code: Optional[str] = None
    referred_by: Optional[int] = None
    total_referrals: int = 0
    balance: float = 0.0

@dataclass
class History:
    id: int
    user_id: int
    message: str
    response: str
    model: str
    timestamp: datetime = None

@dataclass
class Premium:
    id: int
    user_id: int
    plan: str
    price: float
    duration: int
    start_date: datetime
    end_date: datetime
    status: str = "active"
