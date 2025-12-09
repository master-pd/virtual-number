#!/usr/bin/env python3
"""
Virtual Number Generator Bot
GitHub: https://github.com/master-pd/virtual-number-bot
"""

import logging
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.bot import VirtualNumberBot
from src.utils.backup import BackupManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def print_banner():
    """Print ASCII banner"""
    banner = """
╔══════════════════════════════════════════════════════╗
║      📱 VIRTUAL NUMBER GENERATOR BOT                 ║
║      ⚠️ CREATOR : MAR PD MASTER 🪓                  ║
║      🤖 Version: 2.0.0                              ║
║      🐍 Python: 3.8+                                 ║
╚══════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Main entry point"""
    print_banner()
    logger.info("Starting Virtual Number Bot...")
    
    try:
        # Initialize backup manager
        backup = BackupManager()
        backup.start_auto_backup()
        
        # Initialize and start bot
        bot = VirtualNumberBot()
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        print("\n👋 Bot stopped successfully!")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()