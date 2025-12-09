"""
Backup Manager for Virtual Number Bot
"""

import sqlite3
import shutil
import os
import schedule
import time
import json
from datetime import datetime, timedelta
import threading
from typing import Optional, Dict, List
import gzip
import hashlib

class BackupManager:
    def __init__(self, db_path: str = "database/numbers.db", 
                 backup_dir: str = "backups"):
        """Initialize backup manager"""
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.backup_count = 0
        
        # Create backup directory if not exists
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Create backup logs directory
        os.makedirs(os.path.join(self.backup_dir, "logs"), exist_ok=True)
    
    def create_backup(self, backup_type: str = "manual") -> Dict:
        """Create a database backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(
                self.backup_dir, 
                f"backup_{timestamp}_{backup_type}.db.gz"
            )
            
            # Create compressed backup
            with open(self.db_path, 'rb') as f_in:
                with gzip.open(backup_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Get file info
            file_size = os.path.getsize(backup_file)
            
            # Create backup info
            backup_info = {
                "backup_id": timestamp,
                "file_path": backup_file,
                "file_size": file_size,
                "backup_type": backup_type,
                "created_at": datetime.now().isoformat(),
                "status": "success",
                "checksum": self.calculate_checksum(backup_file)
            }
            
            # Save backup info
            self.save_backup_info(backup_info)
            
            # Clean old backups
            self.clean_old_backups()
            
            self.backup_count += 1
            print(f"✅ Backup created: {backup_file} ({file_size:,} bytes)")
            
            return backup_info
            
        except Exception as e:
            error_info = {
                "status": "error",
                "error": str(e),
                "created_at": datetime.now().isoformat()
            }
            self.save_backup_info(error_info)
            print(f"❌ Backup failed: {e}")
            return error_info
    
    def calculate_checksum(self, file_path: str) -> str:
        """Calculate MD5 checksum of a file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def save_backup_info(self, info: Dict):
        """Save backup information to JSON"""
        backup_log = os.path.join(self.backup_dir, "logs", "backup_history.json")
        
        # Load existing logs
        if os.path.exists(backup_log):
            with open(backup_log, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Add new log
        logs.append(info)
        
        # Keep only last 100 logs
        if len(logs) > 100:
            logs = logs[-100:]
        
        # Save logs
        with open(backup_log, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def clean_old_backups(self, keep_days: int = 7, keep_count: int = 10):
        """Clean old backup files"""
        try:
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.endswith(".db.gz") and file.startswith("backup_"):
                    file_path = os.path.join(self.backup_dir, file)
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    backup_files.append((file_path, mod_time))
            
            # Sort by modification time (oldest first)
            backup_files.sort(key=lambda x: x[1])
            
            # Remove by age
            now = datetime.now()
            for file_path, mod_time in backup_files:
                age = now - mod_time
                if age.days > keep_days:
                    os.remove(file_path)
                    print(f"🗑️ Removed old backup: {file_path}")
            
            # Remove by count (keep only latest N)
            backup_files.sort(key=lambda x: x[1], reverse=True)  # newest first
            for i, (file_path, _) in enumerate(backup_files):
                if i >= keep_count:
                    os.remove(file_path)
                    print(f"🗑️ Removed excess backup: {file_path}")
                    
        except Exception as e:
            print(f"❌ Error cleaning backups: {e}")
    
    def restore_backup(self, backup_file: str) -> bool:
        """Restore database from backup"""
        try:
            # Check if backup exists
            if not os.path.exists(backup_file):
                print(f"❌ Backup file not found: {backup_file}")
                return False
            
            # Close existing database connections
            # (This is important for SQLite)
            
            # Create backup of current database
            temp_backup = f"{self.db_path}.temp_backup"
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, temp_backup)
                print(f"📋 Current DB backed up to: {temp_backup}")
            
            # Restore from compressed backup
            with gzip.open(backup_file, 'rb') as f_in:
                with open(self.db_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            print(f"✅ Database restored from: {backup_file}")
            
            # Verify restoration
            if self.verify_database():
                print("✅ Database verification successful")
                # Remove temp backup
                if os.path.exists(temp_backup):
                    os.remove(temp_backup)
                return True
            else:
                print("❌ Database verification failed, restoring from temp backup")
                # Restore from temp backup
                if os.path.exists(temp_backup):
                    shutil.copy2(temp_backup, self.db_path)
                    os.remove(temp_backup)
                return False
                
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def verify_database(self) -> bool:
        """Verify database integrity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if tables exist
            required_tables = ['users', 'user_limits', 'numbers_history']
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            for table in required_tables:
                if table not in existing_tables:
                    print(f"❌ Missing table: {table}")
                    conn.close()
                    return False
            
            # Check database integrity
            cursor.execute("PRAGMA integrity_check;")
            result = cursor.fetchone()[0]
            
            conn.close()
            
            if result == "ok":
                return True
            else:
                print(f"❌ Database integrity check failed: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Database verification error: {e}")
            return False
    
    def start_auto_backup(self, interval_hours: int = 6):
        """Start automatic backup scheduler"""
        def backup_job():
            print(f"⏰ Running scheduled backup at {datetime.now()}")
            self.create_backup("auto")
        
        # Schedule backup
        schedule.every(interval_hours).hours.do(backup_job)
        
        # Run scheduler in background thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
        
        print(f"✅ Auto-backup scheduled every {interval_hours} hours")
    
    def get_backup_list(self) -> List[Dict]:
        """Get list of all backups"""
        backups = []
        
        try:
            for file in os.listdir(self.backup_dir):
                if file.endswith(".db.gz") and file.startswith("backup_"):
                    file_path = os.path.join(self.backup_dir, file)
                    file_size = os.path.getsize(file_path)
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    backups.append({
                        "filename": file,
                        "file_path": file_path,
                        "file_size": file_size,
                        "modified": mod_time.isoformat(),
                        "age_days": (datetime.now() - mod_time).days
                    })
            
            # Sort by modification time (newest first)
            backups.sort(key=lambda x: x["modified"], reverse=True)
            
        except Exception as e:
            print(f"❌ Error getting backup list: {e}")
        
        return backups
    
    def export_to_json(self, output_file: str = "database_export.json"):
        """Export database to JSON format"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            export_data = {
                "export_date": datetime.now().isoformat(),
                "database": self.db_path,
                "tables": {}
            }
            
            # Export each table
            for table in tables:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                table_data = []
                for row in rows:
                    table_data.append(dict(row))
                
                export_data["tables"][table] = table_data
            
            # Save to JSON
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            conn.close()
            
            print(f"✅ Database exported to: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False