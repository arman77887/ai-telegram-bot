import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = 'users.db'):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language_code TEXT DEFAULT 'en',
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_premium BOOLEAN DEFAULT 0,
                    premium_expiry TIMESTAMP,
                    daily_used INTEGER DEFAULT 0,
                    daily_date TIMESTAMP DEFAULT CURRENT_DATE,
                    theme TEXT DEFAULT 'light',
                    is_banned BOOLEAN DEFAULT 0,
                    referral_code TEXT UNIQUE,
                    referred_by INTEGER,
                    total_referrals INTEGER DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    user_id INTEGER PRIMARY KEY,
                    added_by INTEGER,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credits (
                    user_id INTEGER PRIMARY KEY,
                    balance REAL DEFAULT 0,
                    total_earned REAL DEFAULT 0,
                    total_spent REAL DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT,
                    response TEXT,
                    model TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS premium (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    plan TEXT,
                    price REAL,
                    duration INTEGER,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER,
                    referred_user_id INTEGER,
                    commission REAL,
                    status TEXT DEFAULT 'pending',
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL,
                    currency TEXT DEFAULT 'USD',
                    payment_method TEXT,
                    status TEXT DEFAULT 'pending',
                    transaction_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT,
                    message TEXT,
                    user_id INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def register_user(self, user_id: int, username: str = None, first_name: str = None, 
                     last_name: str = None, language_code: str = 'en', referred_by: int = None):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
                if cursor.fetchone():
                    return True
                
                referral_code = f"{user_id}{datetime.now().strftime('%Y%m%d')}"
                cursor.execute('''
                    INSERT INTO users (user_id, username, first_name, last_name, language_code, referral_code, referred_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name, language_code, referral_code, referred_by))
                
                cursor.execute('INSERT INTO credits (user_id, balance) VALUES (?, ?)', (user_id, 0))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error registering user: {e}")
            return False
    
    def get_user(self, user_id: int):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.*, c.balance, c.total_earned, c.total_spent
                    FROM users u
                    LEFT JOIN credits c ON u.user_id = c.user_id
                    WHERE u.user_id = ?
                ''', (user_id,))
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user_usage(self, user_id: int):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                today = datetime.now().date()
                cursor.execute('''
                    UPDATE users 
                    SET daily_used = daily_used + 1, daily_date = ?
                    WHERE user_id = ? AND (daily_date < ? OR daily_date IS NULL)
                ''', (today, user_id, today))
                if cursor.rowcount == 0:
                    cursor.execute('UPDATE users SET daily_used = daily_used + 1 WHERE user_id = ?', (user_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating usage: {e}")
            return False
    
    def get_daily_usage(self, user_id: int):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                today = datetime.now().date()
                cursor.execute('SELECT daily_used FROM users WHERE user_id = ? AND daily_date = ?', (user_id, today))
                row = cursor.fetchone()
                return row[0] if row else 0
        except Exception as e:
            print(f"Error getting usage: {e}")
            return 0
    
    def add_credits(self, user_id: int, amount: float):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE credits SET balance = balance + ?, total_earned = total_earned + ? WHERE user_id = ?', 
                             (amount, amount, user_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding credits: {e}")
            return False
    
    def is_premium(self, user_id: int):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT is_premium, premium_expiry FROM users WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                if not row:
                    return False
                if row[0] and row[1]:
                    expiry = datetime.fromisoformat(row[1])
                    if expiry > datetime.now():
                        return True
                return False
        except Exception as e:
            print(f"Error checking premium: {e}")
            return False
    
    def set_premium(self, user_id: int, plan: str, duration: int, price: float):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                start_date = datetime.now()
                end_date = start_date + timedelta(days=duration)
                cursor.execute('''
                    INSERT INTO premium (user_id, plan, price, duration, start_date, end_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'active')
                ''', (user_id, plan, price, duration, start_date, end_date))
                cursor.execute('UPDATE users SET is_premium = 1, premium_expiry = ? WHERE user_id = ?', (end_date, user_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error setting premium: {e}")
            return False
    
    def is_admin(self, user_id: int):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error checking admin: {e}")
            return False
    
    def add_admin(self, user_id: int, added_by: int):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT OR REPLACE INTO admins (user_id, added_by) VALUES (?, ?)', (user_id, added_by))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding admin: {e}")
            return False
    
    def ban_user(self, user_id: int):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error banning user: {e}")
            return False
    
    def unban_user(self, user_id: int):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error unbanning user: {e}")
            return False
    
    def delete_user(self, user_id: int):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                tables = ['users', 'credits', 'history', 'premium', 'referrals', 'payments', 'conversations']
                for table in tables:
                    cursor.execute(f'DELETE FROM {table} WHERE user_id = ?', (user_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def get_statistics(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM users')
                total_users = cursor.fetchone()[0]
                today = datetime.now().date()
                cursor.execute('SELECT COUNT(*) FROM users WHERE date(registration_date) = ?', (today,))
                today_users = cursor.fetchone()[0]
                cursor.execute('SELECT COUNT(*) FROM users WHERE is_premium = 1 AND premium_expiry > datetime("now")')
                premium_users = cursor.fetchone()[0]
                cursor.execute('SELECT COUNT(*) FROM history')
                total_chats = cursor.fetchone()[0]
                cursor.execute('SELECT SUM(balance) FROM credits')
                total_credits = cursor.fetchone()[0] or 0
                return {
                    'total_users': total_users,
                    'today_users': today_users,
                    'premium_users': premium_users,
                    'total_chats': total_chats,
                    'total_credits': total_credits
                }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def search_users(self, query: str):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM users 
                    WHERE username LIKE ? OR user_id LIKE ? OR first_name LIKE ?
                    LIMIT 50
                ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"Error searching users: {e}")
            return []
    
    def get_all_users(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT user_id FROM users')
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def get_history(self, user_id: int, limit: int = 50):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?', (user_id, limit))
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
    
    def delete_history(self, user_id: int):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM history WHERE user_id = ?', (user_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting history: {e}")
            return False
    
    def save_conversation(self, user_id: int, session_id: str, role: str, content: str):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO conversations (user_id, session_id, role, content) VALUES (?, ?, ?, ?)',
                             (user_id, session_id, role, content))
                conn.commit()
        except Exception as e:
            print(f"Error saving conversation: {e}")
    
    def get_conversation_history(self, user_id: int, session_id: str, limit: int = 10):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT role, content FROM conversations 
                    WHERE user_id = ? AND session_id = ?
                    ORDER BY timestamp DESC LIMIT ?
                ''', (user_id, session_id, limit))
                rows = cursor.fetchall()
                return [{'role': row[0], 'content': row[1]} for row in rows][::-1]
        except Exception as e:
            print(f"Error getting conversation: {e}")
            return []
