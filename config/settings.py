"""
Configuration settings for Virtual Number Bot
"""

import os
from typing import Dict, List, Any
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Bot configuration settings"""
    
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "")
    BOT_NAME: str = os.getenv("BOT_NAME", "Virtual Number Bot")
    
    # Admin Configuration
    ADMIN_IDS: List[int] = [
        int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") 
        if id.strip().isdigit()
    ]
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "")
    
    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "database/numbers.db")
    BACKUP_DIR: str = os.getenv("BACKUP_DIR", "backups")
    BACKUP_INTERVAL: int = int(os.getenv("BACKUP_INTERVAL", "3600"))  # seconds
    
    # Bot Limits
    DEFAULT_USER_LIMIT: int = int(os.getenv("DEFAULT_LIMIT", "10"))
    MAX_EXTRA_LIMIT: int = int(os.getenv("MAX_EXTRA", "50"))
    DAILY_REQUEST_LIMIT: int = int(os.getenv("DAILY_LIMIT", "100"))
    
    # Number Generation
    NUMBER_PREFIXES: List[str] = [
        '70', '71', '72', '73', '74', '75', '76', '77', '78', '79',
        '80', '81', '82', '83', '84', '85', '86', '87', '88', '89',
        '90', '91', '92', '93', '94', '95', '96', '97', '98', '99'
    ]
    OTP_LENGTH: int = 6
    NUMBER_VALIDITY_HOURS: int = 24
    
    # Subscription Channels
    @staticmethod
    def get_channels() -> Dict[str, Any]:
        """Get channel configuration"""
        try:
            with open('config/channels.json', 'r') as f:
                return json.load(f)
        except:
            return {
                "required": [
                    {
                        "id": "@your_channel",
                        "name": "Main Channel",
                        "url": "https://t.me/your_channel"
                    }
                ],
                "optional": []
            }
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/bot.log")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Webhook (for production)
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_PORT: int = int(os.getenv("WEBHOOK_PORT", "8443"))
    
    # Security
    ENABLE_RATE_LIMIT: bool = os.getenv("ENABLE_RATE_LIMIT", "True") == "True"
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # seconds
    
    # Messages
    @staticmethod
    def get_messages() -> Dict[str, str]:
        """Get bot messages"""
        return {
            "welcome": """
🎉 *স্বাগতম ভার্চুয়াল নাম্বার জেনারেটর বটে!*

🤖 *এই বট থেকে আপনি পাবেন:*
✅ ভার্চুয়াল ইন্ডিয়ান নাম্বার
✅ OTP/ভেরিফিকেশন কোড
✅ আপনার অ্যাপে ব্যবহারের জন্য

📊 *লিমিট সিস্টেম:*
• প্রতিজন ইউজার পাবে: *১০টি নাম্বার + ১০টি OTP*
• বেশি চাইলে এডমিনের সাথে যোগাযোগ করুন

🛠️ *কমান্ডস:*
/number - নতুন নাম্বার চাই
/mynumbers - আমার নাম্বারগুলো
/mystatus - আমার স্ট্যাটাস
/contact - এডমিনের সাথে যোগাযোগ
/help - এই মেসেজ
            """,
            
            "number_success": """
✅ *নাম্বার জেনারেট সফল!*

📱 *ইন্ডিয়ান নাম্বার:* 
`{number}`

🔐 *OTP/ভেরিফিকেশন কোড:*
`{otp}`

⏰ *ভ্যালিডিটি:* ২৪ ঘণ্টা
📝 *ব্যবহার:* আপনার অ্যাপে এই নাম্বার ব্যবহার করুন

📊 *আপনার স্ট্যাটাস:*
• ব্যবহৃত: {used}/{total}
• বাকি: {remaining}
            """,
            
            "limit_reached": """
❌ *আপনার লিমিট শেষ হয়েছে!*

📊 *আপনার স্ট্যাটাস:*
• ব্যবহৃত: {used}/{total}
• বাকি: {remaining}

📞 *এডমিনের সাথে যোগাযোগ করুন:*
@{} - আরো নাম্বার চাইলে
            """,
            
            "admin_contact": """
📞 *এডমিনের সাথে যোগাযোগ*

আরো নাম্বার চাইলে বা কোনো সমস্যায় এডমিনের সাথে সরাসরি যোগাযোগ করুন:

👤 এডমিন: @{}

অথবা নিচের বাটনে ক্লিক করুন:
            """
        }
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")
        
        if not cls.ADMIN_IDS:
            errors.append("At least one ADMIN_ID is required")
        
        if errors:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def print_summary(cls):
        """Print configuration summary"""
        print("\n" + "="*50)
        print("🤖 Bot Configuration Summary")
        print("="*50)
        print(f"Bot Name: {cls.BOT_NAME}")
        print(f"Bot Username: {cls.BOT_USERNAME}")
        print(f"Admin IDs: {cls.ADMIN_IDS}")
        print(f"Database: {cls.DATABASE_PATH}")
        print(f"Default Limit: {cls.DEFAULT_USER_LIMIT}")
        print(f"Backup Interval: {cls.BACKUP_INTERVAL} seconds")
        print("="*50 + "\n")

# Create settings instance
settings = Settings()