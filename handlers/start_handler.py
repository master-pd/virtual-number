from telebot import types
import json
import os

def register_start_handlers(bot, db, user_manager):
    
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        """Handle /start command"""
        user = message.from_user
        user_data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'language_code': user.language_code,
            'is_premium': user.is_premium or False,
            'is_bot': user.is_bot
        }
        
        # Register user
        user_manager.register_user(user_data)
        
        # Welcome message
        welcome_text = """
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

⚠️ *সতর্কতা:*
শুধুমাত্র বৈধ কাজে ব্যবহার করুন
        """
        
        # Create inline keyboard
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        btn1 = types.InlineKeyboardButton("📱 নাম্বার নিন", callback_data="get_number")
        btn2 = types.InlineKeyboardButton("📊 আমার স্ট্যাটাস", callback_data="my_status")
        btn3 = types.InlineKeyboardButton("📋 নিয়মাবলী", callback_data="show_rules")
        btn4 = types.InlineKeyboardButton("👑 এডমিন", url=f"https://t.me/{os.getenv('ADMIN_USERNAME', '')}")
        
        markup.add(btn1, btn2, btn3, btn4)
        
        bot.reply_to(
            message,
            welcome_text,
            parse_mode='Markdown',
            reply_markup=markup
        )
    
    @bot.message_handler(commands=['mystatus'])
    def show_status(message):
        """Show user's status"""
        user_id = message.from_user.id
        status = user_manager.get_user_status(user_id)
        
        if not status:
            bot.reply_to(message, "❌ আপনার তথ্য পাওয়া যায়নি। /start দিন")
            return
        
        limits = status['limits']
        user_info = status['user_info']
        
        status_text = f"""
📊 *আপনার অ্যাকাউন্ট স্ট্যাটাস*

👤 ব্যবহারকারী: @{user_info.get('username', 'N/A')}
📅 যোগদান: {user_info.get('join_date', 'N/A')}

📈 *লিমিট বিবরণ:*
• ডিফল্ট লিমিট: {limits.get('max_limit', 10)}
• ব্যবহৃত: {limits.get('used', 0)}
• বাকি: {limits.get('remaining', 10)}
• এক্সট্রা প্রাপ্ত: {limits.get('extra_given', 0)}
• সর্বমোট লিমিট: {limits.get('total_allowed', 10)}
• সর্বশেষ রিসেট: {limits.get('last_reset', 'N/A')}

💡 *টিপস:*
আরো নাম্বার চাইলে এডমিনের সাথে যোগাযোগ করুন
        """
        
        bot.reply_to(message, status_text, parse_mode='Markdown')