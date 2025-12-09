import os
from typing import List, Dict
from datetime import datetime

class AdminManager:
    def __init__(self, db):
        """Initialize admin manager"""
        self.db = db
        self.admin_ids = self._load_admin_ids()
    
    def _load_admin_ids(self) -> List[int]:
        """Load admin IDs from environment or config"""
        admin_str = os.getenv("ADMIN_IDS", "")
        if admin_str:
            return [int(id.strip()) for id in admin_str.split(",") if id.strip().isdigit()]
        return []
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.admin_ids
    
    def add_admin_log(self, admin_id: int, action: str, target_user: int, details: str = ""):
        """Log admin action"""
        self.db.cursor.execute('''
        INSERT INTO admin_logs (admin_id, action, target_user, details)
        VALUES (?, ?, ?, ?)
        ''', (admin_id, action, target_user, details))
        self.db.conn.commit()
    
    def update_user_limit(self, admin_id: int, target_user: int, new_limit: int) -> Dict:
        """Update user's limit (admin action)"""
        if not self.is_admin(admin_id):
            return {'success': False, 'error': 'Not authorized'}
        
        if self.db.update_user_limit(target_user, new_limit):
            self.add_admin_log(
                admin_id, 
                'UPDATE_LIMIT', 
                target_user, 
                f"Set limit to {new_limit}"
            )
            return {'success': True, 'message': f'Limit updated to {new_limit}'}
        
        return {'success': False, 'error': 'Database error'}
    
    def add_extra_numbers(self, admin_id: int, target_user: int, extra_count: int) -> Dict:
        """Add extra numbers to user (admin action)"""
        if not self.is_admin(admin_id):
            return {'success': False, 'error': 'Not authorized'}
        
        if self.db.add_extra_numbers(target_user, extra_count):
            self.add_admin_log(
                admin_id, 
                'ADD_EXTRA', 
                target_user, 
                f"Added {extra_count} extra numbers"
            )
            return {'success': True, 'message': f'Added {extra_count} extra numbers'}
        
        return {'success': False, 'error': 'Database error'}
    
    def get_admin_stats(self) -> Dict:
        """Get detailed statistics for admin"""
        stats = self.db.get_stats()
        
        # Add additional admin stats
        self.db.cursor.execute('''
        SELECT COUNT(DISTINCT user_id) FROM numbers_history 
        WHERE DATE(created_at) = DATE('now')
        ''')
        stats['unique_users_today'] = self.db.cursor.fetchone()[0]
        
        self.db.cursor.execute('''
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as count
        FROM numbers_history 
        GROUP BY DATE(created_at) 
        ORDER BY date DESC 
        LIMIT 7
        ''')
        stats['weekly_trend'] = [dict(row) for row in self.db.cursor.fetchall()]
        
        return stats
    
    def get_user_search(self, search_term: str) -> List[Dict]:
        """Search users by username or ID"""
        try:
            if search_term.isdigit():
                # Search by user ID
                self.db.cursor.execute('''
                SELECT u.*, ul.* 
                FROM users u 
                LEFT JOIN user_limits ul ON u.user_id = ul.user_id 
                WHERE u.user_id = ?
                ''', (int(search_term),))
            else:
                # Search by username
                self.db.cursor.execute('''
                SELECT u.*, ul.* 
                FROM users u 
                LEFT JOIN user_limits ul ON u.user_id = ul.user_id 
                WHERE u.username LIKE ?
                ''', (f'%{search_term}%',))
            
            return [dict(row) for row in self.db.cursor.fetchall()]
        except:
            return []