from typing import Optional, Dict, List
from datetime import datetime

class UserManager:
    def __init__(self, db):
        """Initialize user manager"""
        self.db = db
    
    def register_user(self, user_data: Dict) -> bool:
        """Register new user"""
        return self.db.add_user(
            user_id=user_data['id'],
            username=user_data.get('username'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name', ''),
            language_code=user_data.get('language_code', ''),
            is_premium=user_data.get('is_premium', False),
            is_bot=user_data.get('is_bot', False)
        )
    
    def get_user_status(self, user_id: int) -> Dict:
        """Get user's current status and limits"""
        limits = self.db.get_user_limits(user_id)
        
        if not limits:
            # Create default limits
            self.db.cursor.execute('INSERT OR IGNORE INTO user_limits (user_id) VALUES (?)', (user_id,))
            self.db.conn.commit()
            limits = self.db.get_user_limits(user_id)
        
        # Get user info
        self.db.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user_info = self.db.cursor.fetchone()
        
        return {
            'user_info': dict(user_info) if user_info else {},
            'limits': limits,
            'can_get_more': self.db.can_get_number(user_id)
        }
    
    def request_number(self, user_id: int, app_name: str = "Unknown") -> Optional[Dict]:
        """Process number request for user"""
        from .number_generator import NumberGenerator
        
        # Check if user can get more numbers
        if not self.db.can_get_number(user_id):
            return None
        
        # Generate number and OTP
        generator = NumberGenerator()
        number, otp = generator.generate_virtual_pair()
        
        # Save to database
        if self.db.add_number_to_history(user_id, number, otp, app_name):
            return {
                'success': True,
                'number': number,
                'otp': otp,
                'formatted': generator.format_number_display(number, otp),
                'status': self.get_user_status(user_id)
            }
        
        return None
    
    def get_user_history(self, user_id: int) -> List[Dict]:
        """Get user's number history"""
        return self.db.get_user_numbers(user_id)
    
    def reset_user_limits(self, user_id: int) -> bool:
        """Reset user's used count (admin only)"""
        try:
            self.db.cursor.execute('''
            UPDATE user_limits 
            SET used = 0, 
                remaining = max_limit + extra_given 
            WHERE user_id = ?
            ''', (user_id,))
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error resetting limits: {e}")
            return False