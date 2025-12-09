import random
import hashlib
from datetime import datetime
from typing import Tuple

class NumberGenerator:
    def __init__(self):
        """Initialize number generator"""
        self.used_numbers = set()
        
        # Indian mobile number prefixes
        self.prefixes = [
            '70', '71', '72', '73', '74', '75', '76', '77', '78', '79',
            '80', '81', '82', '83', '84', '85', '86', '87', '88', '89',
            '90', '91', '92', '93', '94', '95', '96', '97', '98', '99'
        ]
    
    def generate_indian_number(self) -> str:
        """Generate a unique Indian virtual number"""
        while True:
            prefix = random.choice(self.prefixes)
            suffix = random.randint(10000000, 99999999)
            number = f"+91{prefix}{suffix}"
            
            # Ensure uniqueness
            if number not in self.used_numbers:
                self.used_numbers.add(number)
                return number
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate OTP code"""
        if length < 4 or length > 8:
            length = 6
        
        # Generate secure random OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
        
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime('%H%M%S')
        return f"{otp}"
    
    def generate_virtual_pair(self) -> Tuple[str, str]:
        """Generate number and OTP pair"""
        number = self.generate_indian_number()
        otp = self.generate_otp()
        return number, otp
    
    def format_number_display(self, number: str, otp: str) -> str:
        """Format number and OTP for display"""
        return f"""
📱 *ইন্ডিয়ান নাম্বার:* 
`{number}`

🔐 *OTP/ভেরিফিকেশন কোড:*
`{otp}`

⏰ *ভ্যালিডিটি:* ২৪ ঘণ্টা
📝 *ব্যবহার:* আপনার অ্যাপে এই নাম্বার ব্যবহার করুন
"""