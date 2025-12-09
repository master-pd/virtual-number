from telebot import types
import json

def register_number_handlers(bot, db, user_manager):
    
    @bot.message_handler(commands=['number'])
    def request_number(message):
        """Handle number request"""
        user_id = message.from_user.id
        
        # Check subscription status
        if not check_subscriptions(user_id):
            show_subscription_required(message)
            return
        
        # Process number request
        result = user_manager.request_number(user_id, "Telegram Bot")
        
        if not result or not result.get('success'):
            # Limit reached
            markup = types.InlineKeyboardMarkup()
            contact_btn = types.InlineKeyboardButton(
                "📞 এডমিনের সাথে যোগাযোগ",
                url=f"https://t.me/{os.getenv('ADMIN_USERNAME')}"
            )
            markup.add(contact_btn)
            
            bot.reply_to(
                message,
                "❌ *আপনার লিমিট শেষ হয়েছে!*\n\n"
                "আরো নাম্বার চাইলে এডমিনের সাথে যোগাযোগ করুন।",
                parse_mode='Markdown',
                reply_markup=markup
            )
            return
        
        # Send number and OTP
        number_info = result['formatted']
        status = result['status']['limits']
        
        response = f"""
{number_info}

📊 *আপনার বর্তমান স্ট্যাটাস:*
• ব্যবহৃত: {status['used']}/{status['total_allowed']}
• বাকি: {status['remaining']}

💾 *সংরক্ষিত:* আপনার নাম্বার স্বয়ংক্রিয়ভাবে সংরক্ষিত হয়েছে।
        """
        
        bot.reply_to(message, response, parse_mode='Markdown')
    
    @bot.message_handler(commands=['mynumbers'])
    def show_my_numbers(message):
        """Show user's number history"""
        user_id = message.from_user.id
        numbers = user_manager.get_user_history(user_id)
        
        if not numbers:
            bot.reply_to(message, "📭 আপনি এখনো কোনো নাম্বার পাননি।")
            return
        
        response = "📋 *আপনার নাম্বার সমূহ*\n\n"
        
        for idx, num in enumerate(numbers[:5], 1):
            response += f"*#{idx}*\n"
            response += f"📱: `{num['phone_number']}`\n"
            response += f"🔐: `{num['otp_code']}`\n"
            response += f"📅: {num['created_at'][:10]}\n"
            response += f"📱 অ্যাপ: {num['app_name']}\n"
            response += "─" * 30 + "\n"
        
        if len(numbers) > 5:
            response += f"\n📜 আরো {len(numbers) - 5} টি নাম্বার আছে..."
        
        bot.reply_to(message, response, parse_mode='Markdown')
    
    def check_subscriptions(user_id):
        """Check if user is subscribed to required channels"""
        # Load channels from config
        try:
            with open('config/channels.json', 'r') as f:
                channels = json.load(f)
        except:
            # Default channels for testing
            channels = {
                "required": ["@test_channel_1", "@test_channel_2"],
                "optional": ["@support_channel"]
            }
        
        # In production, implement actual Telegram API checks
        # For now, return True for testing
        return True
    
    def show_subscription_required(message):
        """Show subscription requirement"""
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        # Add channel buttons
        btn1 = types.InlineKeyboardButton("📢 চ্যানেল ১", url="https://t.me/test_channel_1")
        btn2 = types.InlineKeyboardButton("📢 চ্যানেল ২", url="https://t.me/test_channel_2")
        check_btn = types.InlineKeyboardButton("✅ চেক করুন", callback_data="check_subscription")
        
        markup.add(btn1, btn2, check_btn)
        
        bot.reply_to(
            message,
            "📢 *সাবস্ক্রিপশন প্রয়োজন*\n\n"
            "নাম্বার পেতে নিচের চ্যানেলগুলো সাবস্ক্রাইব করুন:",
            parse_mode='Markdown',
            reply_markup=markup
        )