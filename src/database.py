import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class DatabaseManager:
    def __init__(self, db_path: str = "database/numbers.db"):
        """Initialize database connection"""
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Create necessary tables"""
        # Users table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            language_code TEXT,
            is_premium BOOLEAN DEFAULT 0,
            is_bot BOOLEAN DEFAULT 0,
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # User limits table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_limits (
            user_id INTEGER PRIMARY KEY,
            max_limit INTEGER DEFAULT 10,
            used INTEGER DEFAULT 0,
            remaining INTEGER DEFAULT 10,
            extra_given INTEGER DEFAULT 0,
            total_allowed INTEGER GENERATED ALWAYS AS (max_limit + extra_given) VIRTUAL,
            last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        ''')
        
        # Numbers history table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS numbers_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            phone_number TEXT UNIQUE,
            otp_code TEXT,
            app_name TEXT DEFAULT 'Unknown',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP DEFAULT (datetime('now', '+24 hours')),
            is_used BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        ''')
        
        # Admin actions log
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER,
            action TEXT,
            target_user INTEGER,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Subscription tracking
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER,
            channel_id TEXT,
            channel_name TEXT,
            is_subscribed BOOLEAN DEFAULT 0,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, channel_id)
        )
        ''')
        
        self.conn.commit()
    
    def add_user(self, user_id: int, username: str, first_name: str, 
                 last_name: str = "", language_code: str = "", 
                 is_premium: bool = False, is_bot: bool = False):
        """Add a new user to database"""
        try:
            self.cursor.execute('''
            INSERT OR IGNORE INTO users 
            (user_id, username, first_name, last_name, language_code, is_premium, is_bot)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, language_code, is_premium, is_bot))
            
            # Initialize user limits
            self.cursor.execute('''
            INSERT OR IGNORE INTO user_limits (user_id) VALUES (?)
            ''', (user_id,))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
    
    def get_user_limits(self, user_id: int) -> Optional[Dict]:
        """Get user's number limits"""
        self.cursor.execute('''
        SELECT * FROM user_limits WHERE user_id = ?
        ''', (user_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def can_get_number(self, user_id: int) -> bool:
        """Check if user can get more numbers"""
        limits = self.get_user_limits(user_id)
        if not limits:
            return True
        
        return limits['used'] < limits['total_allowed']
    
    def add_number_to_history(self, user_id: int, phone: str, otp: str, app_name: str = "Unknown"):
        """Add number to history and update limits"""
        try:
            # Add to history
            self.cursor.execute('''
            INSERT INTO numbers_history (user_id, phone_number, otp_code, app_name)
            VALUES (?, ?, ?, ?)
            ''', (user_id, phone, otp, app_name))
            
            # Update limits
            self.cursor.execute('''
            UPDATE user_limits 
            SET used = used + 1, 
                remaining = remaining - 1 
            WHERE user_id = ?
            ''', (user_id,))
            
            # Update user activity
            self.cursor.execute('''
            UPDATE users 
            SET last_active = CURRENT_TIMESTAMP 
            WHERE user_id = ?
            ''', (user_id,))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding number: {e}")
            return False
    
    def get_user_numbers(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's number history"""
        self.cursor.execute('''
        SELECT * FROM numbers_history 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
        ''', (user_id, limit))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_user_limit(self, user_id: int, new_limit: int):
        """Update user's max limit (admin only)"""
        try:
            self.cursor.execute('''
            UPDATE user_limits 
            SET max_limit = ?, 
                remaining = ? - used 
            WHERE user_id = ?
            ''', (new_limit, new_limit, user_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating limit: {e}")
            return False
    
    def add_extra_numbers(self, user_id: int, extra: int):
        """Add extra numbers to user (admin only)"""
        try:
            self.cursor.execute('''
            UPDATE user_limits 
            SET extra_given = extra_given + ?, 
                remaining = remaining + ? 
            WHERE user_id = ?
            ''', (extra, extra, user_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding extra: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get bot statistics"""
        stats = {}
        
        # Total users
        self.cursor.execute('SELECT COUNT(*) FROM users')
        stats['total_users'] = self.cursor.fetchone()[0]
        
        # Active today
        self.cursor.execute('''
        SELECT COUNT(*) FROM users 
        WHERE DATE(last_active) = DATE('now')
        ''')
        stats['active_today'] = self.cursor.fetchone()[0]
        
        # Total numbers generated
        self.cursor.execute('SELECT COUNT(*) FROM numbers_history')
        stats['total_numbers'] = self.cursor.fetchone()[0]
        
        # Numbers today
        self.cursor.execute('''
        SELECT COUNT(*) FROM numbers_history 
        WHERE DATE(created_at) = DATE('now')
        ''')
        stats['numbers_today'] = self.cursor.fetchone()[0]
        
        # Top users
        self.cursor.execute('''
        SELECT u.user_id, u.username, ul.used 
        FROM users u 
        JOIN user_limits ul ON u.user_id = ul.user_id 
        ORDER BY ul.used DESC 
        LIMIT 5
        ''')
        stats['top_users'] = [dict(row) for row in self.cursor.fetchall()]
        
        return stats
    
    def close(self):
        """Close database connection"""
        self.conn.close()