import sqlite3

conn = sqlite3.connect('cora.db')
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS feature_flags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) UNIQUE NOT NULL,
        description TEXT,
        enabled BOOLEAN DEFAULT 0,
        rollout_percentage INTEGER DEFAULT 0,
        user_whitelist TEXT,
        user_blacklist TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)

cursor.execute(
    """
    INSERT OR IGNORE INTO feature_flags (name, description, enabled) VALUES
    ('new_dashboard', 'Enhanced dashboard with analytics', 0),
    ('ai_insights', 'AI-powered expense insights', 0),
    ('mobile_receipts', 'Mobile receipt scanning', 0),
    ('team_collaboration', 'Multi-user team features', 0)
    """
)

conn.commit()
print("Feature flags table created successfully!")
conn.close()


