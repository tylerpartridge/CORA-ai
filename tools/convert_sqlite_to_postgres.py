#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/convert_sqlite_to_postgres.py
🎯 PURPOSE: Convert SQLite data to PostgreSQL-compatible SQL with UUID mapping
🔗 IMPORTS: sqlite3, uuid, csv, os, json
📤 EXPORTS: Main script for data migration
"""

import sqlite3
import uuid
import os
import sys
from pathlib import Path

# --- CONFIG ---
SQLITE_DB = os.getenv('SQLITE_DB', str(Path('data/cora.db')))
PG_SQL_OUT = os.getenv('PG_SQL_OUT', 'postgres_data.sql')

# --- UTILS ---
def gen_uuid():
    return str(uuid.uuid4())

def quote(val):
    if val is None:
        return 'NULL'
    if isinstance(val, str):
        return "'" + val.replace("'", "''") + "'"
    return str(val)

def main():
    print(f"Connecting to SQLite DB: {SQLITE_DB}")
    conn = sqlite3.connect(SQLITE_DB)
    cur = conn.cursor()

    # 1. Export users, generate UUIDs
    print("Exporting users and generating UUIDs...")
    cur.execute("SELECT email, hashed_password, created_at, is_active FROM users")
    users = cur.fetchall()
    email_to_uuid = {}
    user_rows = []
    for row in users:
        email, hashed_password, created_at, is_active = row
        user_id = gen_uuid()
        email_to_uuid[email] = user_id
        user_rows.append((user_id, email, hashed_password, created_at, is_active))

    # 2. Write users to SQL
    with open(PG_SQL_OUT, 'w', encoding='utf-8') as f:
        f.write('-- USERS\n')
        for user_id, email, hashed_password, created_at, is_active in user_rows:
            f.write(f"INSERT INTO users (id, email, hashed_password, created_at, is_active) VALUES ("
                    f"{quote(user_id)}, {quote(email)}, {quote(hashed_password)}, {quote(created_at)}, {quote(is_active == 'true')}" + ");\n")

        # 3. Export and write expense_categories
        f.write('\n-- EXPENSE CATEGORIES\n')
        cur.execute("SELECT id, name, description, icon, is_active, created_at FROM expense_categories")
        for row in cur.fetchall():
            f.write(f"INSERT INTO expense_categories (id, name, description, icon, is_active, created_at) VALUES ("
                    + ', '.join(quote(x) for x in row) + ");\n")

        # 4. Export and write expenses (remap user_email to user_id)
        f.write('\n-- EXPENSES\n')
        cur.execute("SELECT id, user_email, amount_cents, currency, category_id, description, vendor, expense_date, payment_method, receipt_url, tags, created_at, updated_at, confidence_score, auto_categorized FROM expenses")
        for row in cur.fetchall():
            (id_, user_email, amount_cents, currency, category_id, description, vendor, expense_date, payment_method, receipt_url, tags, created_at, updated_at, confidence_score, auto_categorized) = row
            user_id = email_to_uuid.get(user_email)
            tags_json = tags if tags is None else tags.replace("'", "''")
            f.write(f"INSERT INTO expenses (id, user_id, amount_cents, currency, category_id, description, vendor, expense_date, payment_method, receipt_url, tags, created_at, updated_at, confidence_score, auto_categorized) VALUES ("
                    f"{id_}, {quote(user_id)}, {quote(amount_cents)}, {quote(currency)}, {quote(category_id)}, {quote(description)}, {quote(vendor)}, {quote(expense_date)}, {quote(payment_method)}, {quote(receipt_url)}, {quote(tags_json)}, {quote(created_at)}, {quote(updated_at)}, {quote(confidence_score)}, {quote(bool(auto_categorized))}" + ");\n")

        # 5. Export and write user_activity (remap user_email)
        f.write('\n-- USER ACTIVITY\n')
        cur.execute("SELECT id, user_email, action, details, timestamp FROM user_activity")
        for row in cur.fetchall():
            id_, user_email, action, details, timestamp = row
            user_id = email_to_uuid.get(user_email)
            f.write(f"INSERT INTO user_activity (id, user_id, action, details, timestamp) VALUES ("
                    f"{id_}, {quote(user_id)}, {quote(action)}, {quote(details)}, {quote(timestamp)}" + ");\n")

        # 6. Export and write feedback (remap user_email)
        f.write('\n-- FEEDBACK\n')
        cur.execute("SELECT id, user_email, category, message, rating, created_at FROM feedback")
        for row in cur.fetchall():
            id_, user_email, category, message, rating, created_at = row
            user_id = email_to_uuid.get(user_email)
            f.write(f"INSERT INTO feedback (id, user_id, category, message, rating, created_at) VALUES ("
                    f"{id_}, {quote(user_id)}, {quote(category)}, {quote(message)}, {quote(rating)}, {quote(created_at)}" + ");\n")

        # 7. Export and write payments (remap user_email)
        f.write('\n-- PAYMENTS\n')
        cur.execute("SELECT id, user_email, stripe_payment_intent_id, amount, currency, status, description, created_at FROM payments")
        for row in cur.fetchall():
            id_, user_email, stripe_payment_intent_id, amount, currency, status, description, created_at = row
            user_id = email_to_uuid.get(user_email)
            f.write(f"INSERT INTO payments (id, user_id, stripe_payment_intent_id, amount, currency, status, description, created_at) VALUES ("
                    f"{id_}, {quote(user_id)}, {quote(str(stripe_payment_intent_id))}, {quote(amount)}, {quote(currency)}, {quote(status)}, {quote(description)}, {quote(created_at)}" + ");\n")

    print(f"Data export complete. Output: {PG_SQL_OUT}")

if __name__ == "__main__":
    main() 