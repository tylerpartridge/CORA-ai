import sqlite3

conn = sqlite3.connect('cora.db')
cursor = conn.cursor()

indexes = [
    "CREATE INDEX IF NOT EXISTS idx_expenses_user_date ON expenses(user_id, expense_date)",
    "CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category)",
    "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
    "CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token)",
    "CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_waitlist_email ON contractor_waitlist(email)",
    "CREATE INDEX IF NOT EXISTS idx_receipts_expense ON receipts(expense_id)"
]

for stmt in indexes:
    try:
        cursor.execute(stmt)
        print(f"Created/verified: {stmt.split('IF NOT EXISTS ')[-1]}")
    except sqlite3.OperationalError as e:
        print(f"Warning: {e} for statement: {stmt}")

conn.commit()
print("Performance indexes added successfully!")
conn.close()


