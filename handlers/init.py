from .start_handler import register_start_handlers
from .number_handler import register_number_handlers
from .admin_handler import register_admin_handlers
from .callback_handler import register_callback_handlers
from .subscription_handler import register_subscription_handlers

def register_handlers(bot, db, user_manager, admin_manager):
    """Register all handlers"""
    register_start_handlers(bot, db, user_manager)
    register_number_handlers(bot, db, user_manager)
    register_admin_handlers(bot, db, admin_manager)
    register_callback_handlers(bot, db, user_manager)
    register_subscription_handlers(bot, db)