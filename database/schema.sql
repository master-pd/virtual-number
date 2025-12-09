-- Database Schema for Virtual Number Bot
-- Version: 1.0.0

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT NOT NULL,
    last_name TEXT,
    language_code TEXT DEFAULT 'en',
    is_premium BOOLEAN DEFAULT 0,
    is_bot BOOLEAN DEFAULT 0,
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_numbers INTEGER DEFAULT 0,
    total_otps INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    CONSTRAINT check_status CHECK (status IN ('active', 'banned', 'premium'))
);

-- User limits table
CREATE TABLE IF NOT EXISTS user_limits (
    user_id INTEGER PRIMARY KEY,
    max_limit INTEGER DEFAULT 10,
    used INTEGER DEFAULT 0,
    remaining INTEGER DEFAULT 10,
    extra_given INTEGER DEFAULT 0,
    total_allowed INTEGER GENERATED ALWAYS AS (max_limit + extra_given) VIRTUAL,
    last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reset_count INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT check_limits CHECK (used >= 0 AND remaining >= 0)
);

-- Numbers history table
CREATE TABLE IF NOT EXISTS numbers_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    phone_number TEXT UNIQUE NOT NULL,
    otp_code TEXT NOT NULL,
    app_name TEXT DEFAULT 'Unknown',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (datetime('now', '+24 hours')),
    is_used BOOLEAN DEFAULT 0,
    used_at TIMESTAMP,
    is_expired BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Admin actions log
CREATE TABLE IF NOT EXISTS admin_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    target_user INTEGER,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT
);

-- Subscription tracking
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    channel_id TEXT NOT NULL,
    channel_name TEXT,
    channel_type TEXT DEFAULT 'telegram',
    is_subscribed BOOLEAN DEFAULT 0,
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    check_count INTEGER DEFAULT 0,
    UNIQUE(user_id, channel_id)
);

-- Bot statistics
CREATE TABLE IF NOT EXISTS bot_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE NOT NULL,
    total_users INTEGER DEFAULT 0,
    new_users INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    numbers_generated INTEGER DEFAULT 0,
    otps_generated INTEGER DEFAULT 0,
    admin_actions INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rate limiting
CREATE TABLE IF NOT EXISTS rate_limits (
    user_id INTEGER PRIMARY KEY,
    request_count INTEGER DEFAULT 0,
    last_request TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    daily_limit INTEGER DEFAULT 100,
    hourly_limit INTEGER DEFAULT 10,
    is_blocked BOOLEAN DEFAULT 0,
    block_reason TEXT,
    block_until TIMESTAMP
);

-- Backup logs
CREATE TABLE IF NOT EXISTS backup_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backup_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'success',
    error_message TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_join_date ON users(join_date);
CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active);
CREATE INDEX IF NOT EXISTS idx_numbers_history_user_id ON numbers_history(user_id);
CREATE INDEX IF NOT EXISTS idx_numbers_history_created_at ON numbers_history(created_at);
CREATE INDEX IF NOT EXISTS idx_admin_logs_timestamp ON admin_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_bot_stats_date ON bot_stats(date);