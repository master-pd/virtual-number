import telebot
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.database import DatabaseManager
from src.number_generator import NumberGenerator
from src.user_manager import UserManager
from src.admin_manager import AdminManager
from handlers import register_handlers

class VirtualNumberBot:
    def __init__(self):
        """Initialize the bot"""
        self.token = os.getenv("BOT_TOKEN")
        if not self.token:
            raise ValueError("BOT_TOKEN not found in environment variables")
        
        self.bot = telebot.TeleBot(self.token)
        self.db = DatabaseManager()
        self.number_gen = NumberGenerator()
        self.user_manager = UserManager(self.db)
        self.admin_manager = AdminManager(self.db)
        
        # Register all handlers
        register_handlers(self.bot, self.db, self.user_manager, self.admin_manager)
        
        print("✅ Bot initialized successfully")
    
    def run(self):
        """Start the bot"""
        print("🚀 Starting bot polling...")
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("📱 Bot is now running. Press Ctrl+C to stop.")
        
        # Start polling
        self.bot.infinity_polling(timeout=20, long_polling_timeout=20)
    
    def stop(self):
        """Stop the bot gracefully"""
        print("🛑 Stopping bot...")
        self.db.close()
        print("👋 Bot stopped successfully")