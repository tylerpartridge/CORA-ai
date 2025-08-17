import sqlite3

conn = sqlite3.connect('cora.db')
cur = conn.cursor()

# Core tables
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER NOT NULL,
        referral_code VARCHAR(32) UNIQUE NOT NULL,
        reward_type VARCHAR(50) DEFAULT 'free_month',
        reward_amount DECIMAL(10,2) DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS referral_invites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER NOT NULL,
        invited_email VARCHAR(255) NOT NULL,
        referral_code VARCHAR(32) NOT NULL,
        status VARCHAR(50) DEFAULT 'sent',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS referral_conversions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referral_code VARCHAR(32) NOT NULL,
        referred_email VARCHAR(255) NOT NULL,
        referred_user_id INTEGER,
        converted BOOLEAN DEFAULT 0,
        conversion_date TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)

# Indexes
indexes = [
    "CREATE INDEX IF NOT EXISTS idx_referral_code ON referrals(referral_code)",
    "CREATE INDEX IF NOT EXISTS idx_referrer ON referrals(referrer_id)",
    "CREATE INDEX IF NOT EXISTS idx_invites_referrer ON referral_invites(referrer_id)",
    "CREATE INDEX IF NOT EXISTS idx_invites_code ON referral_invites(referral_code)",
    "CREATE INDEX IF NOT EXISTS idx_conv_code ON referral_conversions(referral_code)",
    "CREATE INDEX IF NOT EXISTS idx_conv_email ON referral_conversions(referred_email)"
]
for stmt in indexes:
    cur.execute(stmt)

conn.commit()
print("Referral tables and indexes created.")
conn.close()


